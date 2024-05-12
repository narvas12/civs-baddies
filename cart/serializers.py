from rest_framework import serializers
from cart.models import CartItem, WishlistItem
from products.models import Product
from products.serializers import ProductSerializer


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'name', 'image', 'price', 'category', 'discounted_percentage', 'product_tag']  # Include necessary fields


class CartItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    total_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    quantity = serializers.IntegerField()
    discounted_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    discount = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = CartItem
        fields = ['id', 'product', 'total_price', 'quantity', 'discounted_price', 'discount']


class WishlistItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)  # Use the modified ProductSerializer
    class Meta:
        model = WishlistItem
        fields = ['product']