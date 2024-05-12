from django.shortcuts import get_object_or_404
from rest_framework.generics import (
    ListAPIView,
    RetrieveAPIView,
    CreateAPIView,
    DestroyAPIView,
)
from rest_framework import permissions, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied, NotAcceptable, ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView

from products.models import Product
from products.serializers import ProductSerializer
from users.models import Address, CustomUser
from users.serializers import AddressSerializer
from cart.models import CartItem
from cart.serializers import CartItemSerializer


class CheckoutCartView(APIView):
    # permission_classes = (IsAuthenticated,)  # Enforce user authentication

    def get(self, request, customer_id, *args, **kwargs):  # Change user_uuid to customer_id
        try:
            user = CustomUser.objects.get(customer_id=customer_id)  # Change id to customer_id
        except CustomUser.DoesNotExist:
            return Response({'message': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

        # Retrieve default addresses for different types
        addresses = {}
        for address_type_display, address_type_value in Address.ADDRESS_CHOICES:
            try:
                address = Address.objects.get_default_address_by_type(user_id=user, address_type=address_type_value)
                addresses[address_type_display] = AddressSerializer(address).data
            except Address.DoesNotExist:
                addresses[address_type_display] = None

        # Fetch user's cart items and calculate totals
        cart_items = user.cart_items.all()
        total_price, total_quantity, total_discount = self._calculate_cart_totals(cart_items)

        data = {
            "addresses": addresses,
            "items": CartItemSerializer(cart_items, many=True).data,
            "total_price": total_price,
            "total_quantity": total_quantity,
            "total_discount": total_discount,
            "payment_methods": self._get_available_payment_methods(),  # Get available payment methods
        }

        return Response(data, status=status.HTTP_200_OK)

    def _calculate_cart_totals(self, cart_items):
        total_price = 0
        total_quantity = 0
        total_discount = 0
        for cart_item in cart_items:
            item_price = float(cart_item.product.price)
            item_quantity = cart_item.quantity
            item_discount = cart_item.discount

            total_price += (item_price * item_quantity)
            total_quantity += item_quantity
            total_discount += item_discount
        return total_price, total_quantity, total_discount

    def _get_available_payment_methods(self):
        # Implement logic to retrieve available payment methods (e.g., from settings or integrations)
        # This could be a list of strings like ["credit_card", "paypal", "cod"]
        return ["credit_card", "paypal"]  # Example list (replace with your implementation)