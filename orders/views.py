import time
import uuid
from django.shortcuts import get_object_or_404, render
import requests
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView, RetrieveAPIView, UpdateAPIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from notifications.utils import send_order_confirmation_email
from orders.managers import OrderManager
from rest_framework.exceptions import NotFound
from products.models import Product
from .models import Order, OrderItem, Transaction
from .serializers import OrderCreateSerializer, OrderSerializer, OrderItemSerializer, OrderStatusUpdateSerializer, PaymentSerializer, TrendingProductSerializer
from users.models import Address
from cart.models import CartItem
from django.contrib.auth import get_user_model
from core import settings
from django.core.exceptions import ObjectDoesNotExist
from django.db import DatabaseError
import logging



class OrderCreateAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, format=None):
        user = request.user
        cart_items = CartItem.objects.filter(user=user)

        if not cart_items.exists():
            return Response({"message": "No items in the cart."}, status=status.HTTP_400_BAD_REQUEST)

        total_cost = sum(item.total_price for item in cart_items)

        shipping_address_id = request.data.get('shipping_address_id')

        try:
            if shipping_address_id:
                shipping_address = Address.objects.get(pk=shipping_address_id, user=user, address_type=Address.SHIPPING)
            else:
                shipping_address = Address.objects.filter(user=user, address_type=Address.SHIPPING).latest('created_at')
        except Address.DoesNotExist:
            return Response({"message": "Invalid shipping address ID, or default address not found."}, status=status.HTTP_400_BAD_REQUEST)

        order_data = {
            'buyer': user.id,
            'status': Order.PENDING,
            'is_paid': False,
            'shipping_address': shipping_address.pk,
            'payment_reference': str(uuid.uuid4())
        }

        order_serializer = OrderCreateSerializer(data=order_data)
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

            cart_items.delete()

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

            return Response({'order': order_serializer.data, 'payment': payment_data})

        return Response(order_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


logger = logging.getLogger(__name__)

class PaymentAPIView(APIView):

    def post(self, request, order_id):
        """
        Initialize a payment.
        """
        try:
            order = Order.objects.get(pk=order_id)
        except Order.DoesNotExist:
            return Response({'error': 'Invalid order ID.'}, status=status.HTTP_404_NOT_FOUND)

        email = order.buyer.email
        amount = sum(order_item.total for order_item in order.orderitems.all())

        # Convert the amount to an integer in the smallest currency unit
        amount_in_kobo = int(amount * 100)

        paystack_secret_key = settings.PAYSTACK_SECRET_KEY
        payload = {
            'email': email,
            'amount': amount_in_kobo,
            'callback_url': f'http://127.0.0.1:8000/api/v1/orders/payment/{order_id}/callback/',
        }

        headers = {
            'Authorization': f'Bearer {paystack_secret_key}',
            'Content-Type': 'application/json',
        }

        try:
            response = requests.post('https://api.paystack.co/transaction/initialize', json=payload, headers=headers)
            response.raise_for_status()
            data = response.json()
            authorization_url = data.get('data', {}).get('authorization_url')
            return Response({'authorization_url': authorization_url}, status=status.HTTP_200_OK)
        except requests.exceptions.RequestException as e:
            logger.error(f'RequestException during payment initialization: {str(e)}')
            return Response({'error': 'Failed to initialize payment. Please try again.'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f'Unexpected error during payment initialization: {str(e)}')
            return Response({'error': 'An unexpected error occurred during payment initialization.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def get(self, request, order_id):
        """
        Handle payment callback.
        """
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
                        'charged_at': data['data'].get('charged_at', None),
                        'message': data['data'].get('message', ''),
                    }
                )
                return Response({'message': 'Payment successful and transaction recorded.'}, status=status.HTTP_200_OK)
            else:
                return Response({'error': 'Payment verification failed.'}, status=status.HTTP_400_BAD_REQUEST)

        except requests.exceptions.RequestException as e:
            logger.error(f'RequestException during payment verification: {str(e)}')
            return Response({'error': 'Failed to verify payment. Please try again.'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f'Unexpected error during payment verification: {str(e)}')
            return Response({'error': 'An unexpected error occurred during payment verification.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



class UserOrdersView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        try:
            orders_data = Order.objects.get_user_orders_with_items(user)
            return Response(orders_data, status=status.HTTP_200_OK)
        except ObjectDoesNotExist:
            return Response(
                {"error": "Orders not found for the user"},
                status=status.HTTP_404_NOT_FOUND
            )
        except DatabaseError:
            return Response(
                {"error": "Database error occurred"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        except Exception as e:
            return Response(
                {"error": f"An unexpected error occurred: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    

class OrderDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, order_id):
        try:
            order_data = Order.objects.get_buyer_order_details(user=request.user, order_id=order_id)
            return Response(order_data, status=status.HTTP_200_OK)
        except ObjectDoesNotExist:
            return Response({"error": "Order not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": f"An unexpected error occurred: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

class AdminOrderDetailView(APIView):
    serializer_class = OrderSerializer
    # permission_classes = [IsAuthenticated]
    lookup_field = 'id'

    def get(self, request, *args, **kwargs):
        order_id = self.kwargs.get(self.lookup_field)
        try:
            order_data = Order.objects.get_order_details(order_id)
        except Order.DoesNotExist:
            raise NotFound("Order not found")

        return Response(order_data)


class OrderListView(APIView):
    # permission_classes = [IsAuthenticated]
    serializer_class = OrderSerializer

    def get(self, request, *args, **kwargs):
        orders = Order.objects.list_orders()
        return Response(orders)

class OrderItemsListView(ListAPIView):
    serializer_class = OrderItemSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        order_id = self.kwargs['order_id']
        return OrderItem.objects.filter(order__id=order_id, order__buyer=self.request.user)
    

class TrendingProducts(APIView):
    def get(self, request, format=None):
        manager = Order.objects

        trending_products = manager.get_trending_products()

        serializer = TrendingProductSerializer(trending_products, many=True)

        return Response(serializer.data)
    
    
    
class OrderStatusUpdateView(UpdateAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderStatusUpdateSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'id'

    def get_queryset(self):
        return Order.objects.all()

    def get_object(self):
        queryset = self.get_queryset()
        order_id = self.kwargs.get(self.lookup_field)
        try:
            order = queryset.get(id=order_id)
        except Order.DoesNotExist:
            raise NotFound("Order not found")
        return order

    def update(self, request, *args, **kwargs):
        order = self.get_object()
        serializer = self.get_serializer(order, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)