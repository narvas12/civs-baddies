from rest_framework import serializers
from cart.models import CartItem, WishlistItem
from products.models import Product, ProductImage
from products.serializers import ProductSerializer



class ProductImageSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    class Meta:
        model = ProductImage
        fields = ['image']

    def get_image(self, obj):
        return obj.image.url if obj.image else None


class ProductSerializer(serializers.ModelSerializer):
    first_image = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = ['id', 'name', 'first_image', 'price', 'category', 'discounted_percentage', 'product_tag']

    def get_first_image(self, obj):

        first_image = obj.productimage_set.first()  # Use the default related manager
        if first_image:
            return ProductImageSerializer(first_image).data  # Serialize the image using ProductImageSerializer
        return None

class CartItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    total_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    quantity = serializers.IntegerField()
    discounted_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    discount = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    color = serializers.CharField(required=False, allow_blank=True) 
    size = serializers.CharField(required=False, allow_blank=True)   

    class Meta:
        model = CartItem
        fields = ['id', 'product', 'total_price', 'quantity', 'discounted_price', 'discount', 'color', 'size']




class WishlistItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True) 
    class Meta:
        model = WishlistItem
        fields = ['product']