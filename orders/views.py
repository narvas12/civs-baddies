import time
import uuid
from django.shortcuts import get_object_or_404, render
import requests
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from notifications.utils import send_order_confirmation_email
from orders.managers import OrderManager
from products.models import Product
from .models import Order, OrderItem, Transaction
from .serializers import OrderSerializer, OrderItemSerializer, PaymentSerializer, TrendingProductSerializer
from users.models import Address
from cart.models import CartItem
from django.contrib.auth import get_user_model
from core import settings
from django.db import transaction



# Create order using session id from client
class CreateOrderFromCartView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        user = request.user
        session_id = request.data.get('session_id')
        shipping_address_id = request.data.get('shipping_address_id')
        billing_address_id = request.data.get('billing_address_id')

        if not session_id or not shipping_address_id or not billing_address_id:
            return Response({"error": "Session ID, shipping address ID, and billing address ID are required."}, status=status.HTTP_400_BAD_REQUEST)

        shipping_address = get_object_or_404(Address, id=shipping_address_id)
        billing_address = get_object_or_404(Address, id=billing_address_id)
        
        cart_items = CartItem.objects.filter(session_id=session_id, active=True)
        if not cart_items.exists():
            return Response({"error": "No active cart items found for the given session ID."}, status=status.HTTP_400_BAD_REQUEST)

        with transaction.atomic():
            order = Order.create_order(buyer=user, address=shipping_address)
            order.billing_address = billing_address
            order.save()

            for item in cart_items:
                OrderItem.create_order_item(order=order, product=item.product, quantity=item.quantity).save()
                item.active = False
                item.save()

        return Response({"order_id": order.id, "order_number": order.order_number}, status=status.HTTP_201_CREATED)



# Create order using customer id 
class OrderCreateAPIView(APIView):
    # permission_classes = [IsAuthenticated]

    def post(self, request, format=None):
        customer_id = request.data.get('customer_id')

        if not customer_id:
            return Response({"message": "Customer ID is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = get_user_model().objects.get(customer_id=customer_id)
        except get_user_model().DoesNotExist:
            return Response({"message": "User not found."}, status=status.HTTP_400_BAD_REQUEST)

        cart_items = CartItem.objects.filter(user=user)

        if not cart_items.exists():
            return Response({"message": "No items in the cart."}, status=status.HTTP_400_BAD_REQUEST)

        total_cost = sum(item.total_price for item in cart_items)

        try:
            shipping_address = Address.objects.get(user=user, address_type=Address.SHIPPING)
            billing_address = Address.objects.get(user=user, address_type=Address.BILLING)
        except Address.DoesNotExist:
            return Response({"message": "Default shipping or billing address not found."}, status=status.HTTP_400_BAD_REQUEST)

        order_data = {
            'buyer': user.id,
            'status': Order.PENDING,
            'is_paid': False,
            'shipping_address': shipping_address.pk,
            'billing_address': billing_address.pk,
            'payment_reference': str(uuid.uuid4())  
        }

        order_serializer = OrderSerializer(data=order_data)
        if order_serializer.is_valid():
            order_instance = order_serializer.save()

            products = []
            for cart_item in cart_items:
                order_item = OrderItem.objects.create(
                    order=order_instance,
                    product=cart_item.product,
                    quantity=cart_item.quantity,
                    total=cart_item.total_price
                )

                products.append({
                    'name': cart_item.product.name,
                    'price': cart_item.product.price,
                    'image_url': cart_item.product.image
                })

            # cart_items.delete()

            send_order_confirmation_email(
                user=user,
                order_instance=order_instance,
                products=products,
                order_number=order_instance.order_number,  
                total=total_cost  
            )

            payment_data = {
                'amount': int(total_cost),
                'email': user.email,
                'customer': user.get_full_name(),
                'reference': order_data['payment_reference']
            }

            return Response({'order': order_serializer.data, 'payment':payment_data})




class PaymentView(APIView):
    def post(self, request, order_id):
        try:
            order = Order.objects.get(pk=order_id)
        except Order.DoesNotExist:
            return Response({'error': 'Invalid order ID.'}, status=status.HTTP_404_NOT_FOUND)

        email = order.buyer.email

        amount = sum(order_item.total for order_item in order.orderitems.all())

        paystack_secret_key = settings.PAYSTACK_SECRET_KEY
        payload = {
            'email': email,
            'amount': amount,
            'callback_url': 'https://your-domain.com/callback/' + str(order_id), 
        }

        headers = {
            'Authorization': f'Bearer {paystack_secret_key}',
            'Content-Type': 'application/json',
        }

        try:
            response = requests.post('https://api.paystack.co/transaction/initialize', json=payload, headers=headers)
            response.raise_for_status()  

            data = response.json()
            authorization_url = data.get('authorization_url')

            return Response({'authorization_url': authorization_url}, status=status.HTTP_200_OK)

        except requests.exceptions.RequestException as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({'error': 'An unexpected error occurred.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class PaymentCallbackView(APIView):
    def post(self, request, order_id):
        try:
            order = Order.objects.get(pk=order_id)
        except Order.DoesNotExist:
            return Response({'error': 'Invalid order ID.'}, status=status.HTTP_404_NOT_FOUND)


        paystack_secret_key = settings.PAYSTACK_SECRET_KEY

        reference = request.GET.get('reference') 

        headers = {
            'Authorization': f'Bearer {paystack_secret_key}',
        }

        try:
            response = requests.get(f'https://api.paystack.co/transaction/verify/{reference}', headers=headers)
            response.raise_for_status()  

            data = response.json()

            if data['data']['status'] == 'success':
                order.is_paid = True
                order.save()

                transaction, created = Transaction.objects.get_or_create(
                    order=order,
                    reference=reference,
                    defaults={
                        'amount': data['data']['amount'],  
                        'status': data['data']['status'],
                        'charged_at': data['data'].get('charged_at'),
                        'message': data['data'].get('message'),
                    }
                )

        except requests.exceptions.RequestException as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({'error': 'An unexpected error occured'},  status=status.HTTP_400_BAD_REQUEST)



class TrendingProducts(APIView):
    def get(self, request, format=None):
        manager = Order.objects

        trending_products = manager.get_trending_products()

        serializer = TrendingProductSerializer(trending_products, many=True)

        return Response(serializer.data)