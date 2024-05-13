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





class OrderCreateAPIView(APIView):
    # permission_classes = [IsAuthenticated]

    def post(self, request, format=None):
        customer_id = request.data.get('customer_id')

        # Check if the customer_id is provided
        if not customer_id:
            return Response({"message": "Customer ID is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Check if the user exists
            user = get_user_model().objects.get(customer_id=customer_id)
        except get_user_model().DoesNotExist:
            return Response({"message": "User not found."}, status=status.HTTP_400_BAD_REQUEST)

        # Fetch cart items for the customer
        cart_items = CartItem.objects.filter(user=user)

        # Check if there are any cart items
        if not cart_items.exists():
            return Response({"message": "No items in the cart."}, status=status.HTTP_400_BAD_REQUEST)

        total_cost = sum(item.total_price for item in cart_items)

        # Fetch default shipping and billing addresses for the user
        try:
            # Get the default shipping address
            shipping_address = Address.objects.get(user=user, address_type=Address.SHIPPING)
            # Get the default billing address
            billing_address = Address.objects.get(user=user, address_type=Address.BILLING)
        except Address.DoesNotExist:
            return Response({"message": "Default shipping or billing address not found."}, status=status.HTTP_400_BAD_REQUEST)

        # Create order data
        order_data = {
            'buyer': user.id,
            'status': Order.PENDING,
            'is_paid': False,
            'shipping_address': shipping_address.pk,
            'billing_address': billing_address.pk,
            'payment_reference': str(uuid.uuid4())  # Generate a unique payment reference
        }

        # Serialize order data
        order_serializer = OrderSerializer(data=order_data)
        if order_serializer.is_valid():
            # Save order instance
            order_instance = order_serializer.save()

            # Create order items from cart items
            products = []
            for cart_item in cart_items:
                # Create order item and set the order field
                order_item = OrderItem.objects.create(
                    order=order_instance,
                    product=cart_item.product,
                    quantity=cart_item.quantity,
                    total=cart_item.total_price
                )

                # Add product details to the products list
                products.append({
                    'name': cart_item.product.name,
                    'price': cart_item.product.price,
                    'image_url': cart_item.product.image
                })

            # Empty the customer's cart after order creation
            # cart_items.delete()

            # Pass necessary data to send_order_confirmation_email
            send_order_confirmation_email(
                user=user,
                order_instance=order_instance,
                products=products,
                order_number=order_instance.order_number,  # Pass the order number
                total=total_cost  # Pass the total cost
            )

            # Prepare data for Paystack payment initiation (frontend use)
            payment_data = {
                'amount': int(total_cost * 100),  # Convert to kobo for Paystack
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

        serializer = PaymentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']
        amount = serializer.validated_data['amount']


        paystack_secret_key = settings.PAYSTACK_SECRET_KEY
        # Construct Paystack API request payload
        payload = {
            'email': email,
            'amount': amount,
            'callback_url': 'https://your-domain.com/callback/' + str(order_id),  # Include order ID in callback URL
            # ... other parameters (optional)
        }

        headers = {
            'Authorization': f'Bearer {paystack_secret_key}',
            'Content-Type': 'application/json',
        }

        try:
            response = requests.post('https://api.paystack.co/transaction/initialize', json=payload, headers=headers)
            response.raise_for_status()  # Raise an exception for non-2xx status codes

            data = response.json()
            authorization_url = data.get('authorization_url')

            return Response({'authorization_url': authorization_url}, status=status.HTTP_200_OK)

        except requests.exceptions.RequestException as e:
            # Handle API call errors gracefully
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            # Handle unexpected errors
            return Response({'error': 'An unexpected error occurred.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class PaymentCallbackView(APIView):
    def post(self, request, order_id):
        try:
            order = Order.objects.get(pk=order_id)
        except Order.DoesNotExist:
            return Response({'error': 'Invalid order ID.'}, status=status.HTTP_404_NOT_FOUND)


        paystack_secret_key = settings.PAYSTACK_SECRET_KEY

        # Retrieve reference from callback URL or request data (depending on your implementation)
        reference = request.GET.get('reference') 

        headers = {
            'Authorization': f'Bearer {paystack_secret_key}',
        }

        try:
            response = requests.get(f'https://api.paystack.co/transaction/verify/{reference}', headers=headers)
            response.raise_for_status()  # Raise an exception for non-2xx status codes

            data = response.json()

            if data['data']['status'] == 'success':
                order.is_paid = True
                order.save()

                # Update or create transaction
                transaction, created = Transaction.objects.get_or_create(
                    order=order,
                    reference=reference,
                    defaults={
                        'amount': data['data']['amount'] / 100,  # Assuming amount is returned in subunit of currency
                        'status': data['data']['status'],
                        'charged_at': data['data'].get('charged_at'),
                        'message': data['data'].get('message'),
                    }
                )

        except requests.exceptions.RequestException as e:
            # Handle API call errors gracefully
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            # Handle unexpected errors
            return Response({'error': 'An unexpected error occured'},  status=status.HTTP_400_BAD_REQUEST)


class TrendingProducts(APIView):
    def get(self, request, format=None):
        # Get the manager
        manager = Order.objects

        # Get the trending products
        trending_products = manager.get_trending_products()

        # Serialize the data
        serializer = TrendingProductSerializer(trending_products, many=True)

        # Return the serialized data
        return Response(serializer.data)