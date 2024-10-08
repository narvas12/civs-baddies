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
from django.views.decorators.csrf import csrf_exempt
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.timezone import now
import hashlib
import hmac
import requests



class OrderCreateAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, format=None):
        user = request.user
        cart_items = CartItem.objects.filter(user=user)

        if not cart_items.exists():
            return Response({"message": "No items in the cart."}, status=status.HTTP_400_BAD_REQUEST)

        total_cost = sum(item.total_price for item in cart_items)
        shipping_address_id = request.data.get('shipping_address_id')

        shipping_address = self.get_shipping_address(user, shipping_address_id)
        if not shipping_address:
            return Response({"message": "Invalid shipping address ID, or default address not found."}, status=status.HTTP_400_BAD_REQUEST)

        order_data = self.build_order_data(user, shipping_address)
        order_serializer = OrderCreateSerializer(data=order_data)

        if order_serializer.is_valid():
            order_instance = order_serializer.save()
            products = self.create_order_items(order_instance, cart_items)

            # cart_items.delete()

            # Send order confirmation email
            send_order_confirmation_email(
                user=user,
                order_instance=order_instance,
                products=products,
                order_number=order_instance.order_number,
                total=total_cost
            )

            payment_data = self.prepare_payment_data(total_cost, user, order_data['payment_reference'])

            return Response({'order': order_serializer.data, 'payment': payment_data}, status=status.HTTP_201_CREATED)

        return Response(order_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get_shipping_address(self, user, shipping_address_id):
        try:
            if shipping_address_id:
                return Address.objects.get(pk=shipping_address_id, user=user, address_type=Address.SHIPPING)
            return Address.objects.filter(user=user, address_type=Address.SHIPPING).latest('created_at')
        except Address.DoesNotExist:
            return None

    def build_order_data(self, user, shipping_address):
        return {
            'buyer': user.id,
            'status': Order.PENDING,
            'is_paid': False,
            'shipping_address': shipping_address.pk,
            'payment_reference': str(uuid.uuid4())
        }

    def create_order_items(self, order, cart_items):
        products = []
        for cart_item in cart_items:
            # Create order item and pass color and size from cart item
            order_item = OrderItem.create_order_item(
                order=order,
                product=cart_item.product,
                quantity=cart_item.quantity,

                color=cart_item.color,    # Include color
                size=cart_item.size      # Include size
            )
            order_item.save()

            # Get product image if available
            first_image = cart_item.product.productimage_set.first()
            image_url = first_image.image.url if first_image else None

            products.append({
                'name': cart_item.product.name,
                'price': cart_item.product.price,
                'image_url': image_url,
                'color': cart_item.color,  # Include color details
                'size': cart_item    # Include size details
            })

        return products

    def prepare_payment_data(self, total_cost, user, payment_reference):
        return {
            'amount': int(total_cost),
            'email': user.email,
            'customer': user.get_full_name(),
            'reference': payment_reference
        }



logger = logging.getLogger(__name__)


class PaymentAPIView(APIView):
    def post(self, request, order_id):
        order = self.get_order(order_id)
        if not order:
            return Response({'error': 'Invalid order ID.'}, status=status.HTTP_404_NOT_FOUND)

        email = order.buyer.email
        amount_in_kobo = self.calculate_amount_in_kobo(order)

        payload = {
            'email': email,
            'amount': amount_in_kobo,
            'callback_url': f'http://127.0.0.1:8000/api/v1/orders/payment/{order_id}/callback/',
        }

        response = self.initialize_payment(payload)
        if isinstance(response, Response):
            return response

        return Response({'authorization_url': response}, status=status.HTTP_200_OK)

    def get(self, request, order_id):
        order = self.get_order(order_id)
        if not order:
            return Response({'error': 'Invalid order ID.'}, status=status.HTTP_404_NOT_FOUND)

        reference = request.GET.get('reference')
        payment_status, transaction_data = self.verify_payment(reference)

        if payment_status == 'success':
            self.record_transaction(order, transaction_data)
            return Response({'message': 'Payment successful and transaction recorded.'}, status=status.HTTP_200_OK)

        return Response({'error': 'Payment verification failed.'}, status=status.HTTP_400_BAD_REQUEST)

    def get_order(self, order_id):
        try:
            return Order.objects.get(pk=order_id)
        except Order.DoesNotExist:
            return None

    def calculate_amount_in_kobo(self, order):
        return int(sum(order_item.total for order_item in order.orderitems.all()) * 100)

    def initialize_payment(self, payload):
        headers = {
            'Authorization': f'Bearer {settings.PAYSTACK_SECRET_KEY}',
            'Content-Type': 'application/json',
        }

        try:
            response = requests.post('https://api.paystack.co/transaction/initialize', json=payload, headers=headers)
            response.raise_for_status()
            return response.json()['data']['authorization_url']
        except requests.exceptions.RequestException as e:
            logger.error(f'RequestException during payment initialization: {str(e)}')
            return Response({'error': 'Failed to initialize payment. Please try again.'}, status=status.HTTP_400_BAD_REQUEST)

    def verify_payment(self, reference):
        headers = {
            'Authorization': f'Bearer {settings.PAYSTACK_SECRET_KEY}',
        }

        try:
            response = requests.get(f'https://api.paystack.co/transaction/verify/{reference}', headers=headers)
            response.raise_for_status()
            data = response.json()
            return data['data']['status'], data['data']
        except requests.exceptions.RequestException as e:
            logger.error(f'RequestException during payment verification: {str(e)}')
            return None, None

    def record_transaction(self, order, transaction_data):
        Transaction.objects.get_or_create(
            order=order,
            reference=transaction_data['reference'],
            defaults={
                'amount': transaction_data['amount'],
                'status': transaction_data['status'],
                'charged_at': transaction_data.get('charged_at', None),
                'message': transaction_data.get('message', ''),
            }
        )


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
    


@csrf_exempt  # Disable CSRF for webhook since it's from an external source.
def paystack_webhook(request):
    # Ensure the request method is POST
    if request.method == 'POST':
        try:
            # Load the data sent by Paystack
            data = json.loads(request.body)

            # Paystack sends the event data in a field named 'event' and the actual transaction data in 'data'
            event_type = data.get('event')
            event_data = data.get('data')

            # Verify Paystack signature to ensure authenticity
            paystack_secret_key = 'your_secret_key_here'  # Replace with your Paystack secret key
            signature = request.headers.get('x-paystack-signature')
            hash_value = hmac.new(
                paystack_secret_key.encode(),
                msg=request.body,
                digestmod=hashlib.sha512
            ).hexdigest()

            if signature != hash_value:
                return JsonResponse({"error": "Invalid signature"}, status=400)

            # Process the event (example: 'charge.success')
            if event_type == 'charge.success':
                # Retrieve the order associated with the transaction
                reference = event_data['reference']
                amount = event_data['amount'] / 100  # Convert amount to decimal format (Paystack sends in kobo)
                transaction_status = event_data['status']

                try:
                    # Find the transaction by reference
                    transaction = Transaction.objects.get(reference=reference)
                    transaction.status = transaction_status
                    transaction.charged_at = now()
                    transaction.save()

                    # Update the associated order as well
                    if transaction_status == 'success':
                        order = transaction.order
                        order.is_paid = True
                        order.status = Order.COMPLETED  # Update the order status to completed
                        order.save()

                    return JsonResponse({"message": "Webhook received and processed successfully"}, status=200)

                except Transaction.DoesNotExist:
                    return JsonResponse({"error": "Transaction not found"}, status=404)

            return JsonResponse({"message": "Unhandled event"}, status=200)

        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON payload"}, status=400)

    return JsonResponse({"error": "Invalid request method"}, status=405)



@csrf_exempt
def flutterwave_webhook(request):
    if request.method == 'POST':
        try:
            # Parse the incoming JSON request
            data = json.loads(request.body)
            
            # Flutterwave sends the transaction information in the 'data' field
            event_data = data.get('data', {})
            transaction_status = event_data.get('status')
            tx_ref = event_data.get('tx_ref')  # Flutterwave transaction reference
            flw_ref = event_data.get('flw_ref')  # Flutterwave internal reference
            amount = event_data.get('amount')
            charged_at = event_data.get('created_at')

            # Verify the signature using Flutterwave secret hash
            flutterwave_secret_hash = settings.FLUTTERWAVE_SECRETE  # Replace with your secret key
            signature = request.headers.get('verif-hash')
            computed_hash = hmac.new(flutterwave_secret_hash.encode(), request.body, hashlib.sha256).hexdigest()

            if signature != computed_hash:
                return JsonResponse({"error": "Invalid signature"}, status=400)

            # Find the transaction in your database using the `tx_ref` (your internal reference)
            try:
                transaction = Transaction.objects.get(reference=tx_ref)

                # Update the transaction based on the payment status received
                transaction.status = transaction_status
                transaction.flw_ref = flw_ref
                transaction.charged_at = charged_at
                transaction.amount = amount
                transaction.save()

                # If payment was successful, update the corresponding order as well
                if transaction_status == 'successful':
                    order = transaction.order
                    order.is_paid = True
                    order.status = Order.COMPLETED  # Mark order as completed
                    order.save()

                return JsonResponse({"message": "Webhook processed successfully"}, status=200)

            except Transaction.DoesNotExist:
                return JsonResponse({"error": "Transaction not found"}, status=404)

        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON payload"}, status=400)

    return JsonResponse({"error": "Invalid request method"}, status=405)



class BaseWebhook:
    def __init__(self, request):
        self.request = request
        self.data = None
        self.event_type = None
        self.event_data = None

    def load_data(self):
        """ Load JSON data from the request body """
        try:
            self.data = json.loads(self.request.body)
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON payload"}, status=400)

        return None

    def verify_signature(self, signature, secret, hash_function=hashlib.sha512):
        """ Verifies the signature of the request """
        computed_hash = hmac.new(
            secret.encode(),
            msg=self.request.body,
            digestmod=hash_function
        ).hexdigest()
        
        if signature != computed_hash:
            return JsonResponse({"error": "Invalid signature"}, status=400)
        return None

    def find_transaction(self, reference):
        """ Finds a transaction based on the reference """
        try:
            transaction = Transaction.objects.get(reference=reference)
            return transaction, None
        except Transaction.DoesNotExist:
            return None, JsonResponse({"error": "Transaction not found"}, status=404)

    def update_transaction(self, transaction, status, amount=None, charged_at=None):
        """ Updates the transaction with new status and optional fields """
        transaction.status = status
        if amount:
            transaction.amount = amount
        if charged_at:
            transaction.charged_at = charged_at
        transaction.save()

    def update_order(self, transaction, success_status):
        """ Updates the order associated with the transaction """
        if transaction.status == success_status:
            order = transaction.order
            order.is_paid = True
            order.status = Order.COMPLETED
            order.save()

    def process_webhook(self):
        """ This method should be overridden by subclasses to process specific webhook events """
        raise NotImplementedError
    



class PaystackWebhook(BaseWebhook):
    def process_webhook(self):
        # Load data from request
        response = self.load_data()
        if response:
            return response
        
        self.event_type = self.data.get('event')
        self.event_data = self.data.get('data')

        # Verify Paystack signature
        paystack_secret_key = settings.PAYSTACK_SECRET_KEY
        signature = self.request.headers.get('x-paystack-signature')
        response = self.verify_signature(signature, paystack_secret_key)
        if response:
            return response

        # Handle 'charge.success' event
        if self.event_type == 'charge.success':
            reference = self.event_data.get('reference')
            amount = self.event_data.get('amount') / 100  # Convert amount from kobo
            transaction_status = self.event_data.get('status')

            # Find the transaction
            transaction, response = self.find_transaction(reference)
            if response:
                return response

            # Update the transaction and order
            self.update_transaction(transaction, transaction_status, charged_at=now())
            self.update_order(transaction, success_status='success')

            return JsonResponse({"message": "Webhook received and processed successfully"}, status=200)

        return JsonResponse({"message": "Unhandled event"}, status=200)



class FlutterwaveWebhook(BaseWebhook):
    def process_webhook(self):
        # Load data from request
        response = self.load_data()
        if response:
            return response

        self.event_data = self.data.get('data', {})
        transaction_status = self.event_data.get('status')
        tx_ref = self.event_data.get('tx_ref')  # Flutterwave transaction reference
        flw_ref = self.event_data.get('flw_ref')  # Flutterwave internal reference
        amount = self.event_data.get('amount')
        charged_at = self.event_data.get('created_at')

        # Verify Flutterwave signature
        flutterwave_secret_hash = settings.FLUTTERWAVE_SECRET_KEY
        signature = self.request.headers.get('verif-hash')
        response = self.verify_signature(signature, flutterwave_secret_hash, hash_function=hashlib.sha256)
        if response:
            return response

        # Find the transaction
        transaction, response = self.find_transaction(tx_ref)
        if response:
            return response

        # Update the transaction and order
        self.update_transaction(transaction, transaction_status, amount=amount, charged_at=charged_at)
        self.update_order(transaction, success_status='successful')

        return JsonResponse({"message": "Webhook processed successfully"}, status=200)


@csrf_exempt
def paystack_webhook(request):
    """ Handle Paystack webhook """
    handler = PaystackWebhook(request)
    return handler.process_webhook()

@csrf_exempt
def flutterwave_webhook(request):
    """ Handle Flutterwave webhook """
    handler = FlutterwaveWebhook(request)
    return handler.process_webhook()