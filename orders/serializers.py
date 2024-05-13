from rest_framework import serializers
from users.models import Address
from .models import Order, OrderItem



class OrderSerializer(serializers.ModelSerializer):
    shipping_address = serializers.PrimaryKeyRelatedField(queryset=Address.objects.all(), required=True)
    billing_address = serializers.PrimaryKeyRelatedField(queryset=Address.objects.all(), required=True)

    class Meta:
        model = Order
        fields = ['id', 'buyer', 'order_number', 'status', 'is_paid', 'shipping_address', 'billing_address']
        read_only_fields = ['id', 'order_number', 'status', 'is_paid']



class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ['product', 'quantity', 'total']


class PaymentSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    amount = serializers.DecimalField(max_digits=10, decimal_places=2, required=True)


class TrendingProductSerializer(serializers.Serializer):
    product_name = serializers.CharField(source='product__name')
    total_sold = serializers.IntegerField(source='total')