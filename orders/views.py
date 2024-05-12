import time
import uuid
from django.shortcuts import get_object_or_404, render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from notifications.utils import send_order_confirmation_email
from orders.managers import OrderManager
from products.models import Product
from .models import Order, OrderItem
from .serializers import OrderSerializer, OrderItemSerializer, TrendingProductSerializer
from users.models import Address
from cart.models import CartItem
from django.contrib.auth import get_user_model
import pypaystack
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




# Initialize Paystack with your secret key
paystack_secret_key = settings.PAYSTACK_SECRET_KEY
paystack_api = pypaystack.Transaction(settings.PAYSTACK_PUBLIC_KEY)


class PaystackWebhook(APIView):
    def post(self, request, *args, **kwargs):
        event = request.data.get('event')
        data = request.data.get('data')

        # Verify the webhook event with Paystack
        signature = request.headers.get('x-paystack-signature')
        try:
            paystack_api.webhook.verify(signature, data)
        except pypaystack.exceptions.InvalidSignatureError:
            return Response({'error': 'Invalid signature'}, status=status.HTTP_400_BAD_REQUEST)

        # Process the event based on the event type
        if event == 'charge.success':
            # Payment successful, update order status
            try:
                # Retrieve order based on payment reference from Paystack data
                payment_reference = data['reference']
                order = Order.objects.get(payment_reference=payment_reference)

                # Update order status to 'paid' or similar
                order.is_paid = True
                order.save()

                # Send notification or perform other actions (optional)
                # ...

                return Response({'message': 'Payment successful and order updated'}, status=status.HTTP_200_OK)
            except Order.DoesNotExist:
                # Handle case where order not found (log or investigate)
                return Response({'message': 'Order not found for reference'}, status=status.HTTP_400_BAD_REQUEST)

        elif event == 'charge.failure':
            # Payment failed, handle accordingly (optional)
            # ...
            return Response({'message': 'Payment failed'}, status=status.HTTP_200_OK)

        return Response({'error': 'Invalid request'}, status=status.HTTP_400_BAD_REQUEST)


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