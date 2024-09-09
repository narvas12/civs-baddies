from rest_framework import serializers
from products.models import Variation
from users.models import Address
from users.serializers import CustomUserSerializer
from .models import Order, OrderItem


class VariationDetailSerializer(serializers.ModelSerializer):
    colors = serializers.SerializerMethodField()

    class Meta:
        model = Variation
        fields = ['id', 'product_variant', 'colors']

    def get_colors(self, obj):
        return [
            {
                "color_name": color.name,
                "sizes": [
                    {
                        "size_name": size.name,
                        "quantity": size.quantity
                    } for size in color.sizes.all()
                ]
            } for color in obj.colors.all()
        ]

class OrderItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    product_description = serializers.CharField(source='product.description', read_only=True)
    product_image = serializers.ImageField(source='product.image', read_only=True)
    variation = VariationDetailSerializer()
    color = serializers.CharField(source='color.name', read_only=True)  # Add color to the serializer
    size = serializers.CharField(source='size.name', read_only=True)    # Add size to the serializer

    class Meta:
        model = OrderItem
        fields = ['id', 'order', 'product', 'product_name', 'product_description', 'product_image', 'quantity', 'total', 'variation', 'color', 'size']




class OrderSerializer(serializers.ModelSerializer):
    orderitems = OrderItemSerializer(many=True, read_only=True)
    total_cost = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    buyer = CustomUserSerializer()
    
    class Meta:
        model = Order
        fields = ['id', 'buyer', 'order_number', 'status', 'is_paid', 'shipping_address', 'created_at', 'orderitems', 'total_cost']


class OrderCreateSerializer(serializers.ModelSerializer):
    orderitems = OrderItemSerializer(many=True, read_only=True)
    total_cost = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    
    class Meta:
        model = Order
        fields = ['id', 'buyer', 'order_number', 'status', 'is_paid', 'shipping_address', 'created_at', 'orderitems', 'total_cost']


class PaymentSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    amount = serializers.DecimalField(max_digits=10, decimal_places=2, required=True)


class TrendingProductSerializer(serializers.Serializer):
    product_name = serializers.CharField(source='product__name')
    total_sold = serializers.IntegerField(source='total')
    
    
class OrderStatusUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['status']

    def validate_status(self, value):
        if value not in dict(Order.STATUS_CHOICES).keys():
            raise serializers.ValidationError("Invalid status")
        return value