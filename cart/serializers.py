from rest_framework import serializers
from cart.models import CartItem, WishList
from products.models import Product, ProductImage
from products.serializers import ProductSerializer, ProductDetailSerializer
from django.utils.text import slugify


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
    product = ProductDetailSerializer(read_only=True)
    product_id = serializers.IntegerField(write_only=True)
    session_key = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = WishList
        fields = ['id','product', 'product_id', 'slug', 'added_date', 'session_key']

    def create(self, validated_data):
        product_id = validated_data.get('product_id')
        session_key = validated_data.get('session_key')

        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            raise serializers.ValidationError("Product does not exist.")
        
        wishlist_item, created = WishList.objects.get_or_create(
            product=product,
            session_key=session_key,
            defaults={'slug': self.generate_unique_slug(product)}
        )
        
        return wishlist_item

    def generate_unique_slug(self, product):
        import random, string
        slug_base = slugify(f"{product.name}-{product.id}")
        random_suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
        return f"{slug_base}-{random_suffix}"