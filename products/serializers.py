from rest_framework import serializers
from .models import Color, CoverPageCarousel, LatestArival, Product, ProductCategory, ProductImage, Size, Supercategory, Variation, get_default_product_category
from drf_extra_fields.fields import Base64ImageField
from django.contrib.auth import get_user_model
from django.conf import settings
import cloudinary
import random
import string
from cloudinary.uploader import upload

User = get_user_model()

class ImageHandlingMixin:
    def upload_image(self, image):
        cloudinary.config(
            cloud_name=settings.CLOUDINARY_STORAGE['CLOUD_NAME'],
            api_key=settings.CLOUDINARY_STORAGE['API_KEY'],
            api_secret=settings.CLOUDINARY_STORAGE['API_SECRET']
        )

        upload_result = upload(image, folder="product/images/")
        return upload_result['secure_url']

class ProductCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductCategory
        fields = '__all__'

class SupercategoryCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Supercategory
        fields = ['name']

class SupercategorySerializer(serializers.ModelSerializer):
    category = ProductCategorySerializer()
    class Meta:
        model = Supercategory
        fields = ['name', 'category']


class ProductImageSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = ProductImage
        fields = ['id', 'image', 'image_url']

    def get_image_url(self, obj):

        if isinstance(obj.image, str):
            return obj.image  
        return obj.image.url if obj.image else None 
    

class SizeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Size
        fields = ['id', 'name', 'quantity']


class ColorSerializer(serializers.ModelSerializer):
    sizes = SizeSerializer(many=True, required=False)  # Nested SizeSerializer

    class Meta:
        model = Color
        fields = ['id', 'name', 'quantity', 'sizes']


class VariationSerializer(serializers.ModelSerializer):
    colors = ColorSerializer(many=True, required=False)

    class Meta:
        model = Variation
        fields = ['id', 'product_variant', 'colors', 'price']

    def create(self, validated_data):
        colors_data = validated_data.pop('colors', [])
        variation = Variation.objects.create(**validated_data)

        for color_data in colors_data:
            sizes_data = color_data.pop('sizes', [])
            color_id = color_data.get('id')
            
            color, created = Color.objects.get_or_create(id=color_id, defaults=color_data)

            for size_data in sizes_data:
                size_name = size_data.get('name')
                size_quantity = size_data.get('quantity')

                size, created = Size.objects.get_or_create(name=size_name, defaults={'quantity': size_quantity})
                
                if not created:
                    size.quantity = size_quantity
                    size.save()
                
                color.sizes.add(size)

            variation.colors.add(color)

        return variation

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        colors_with_sizes = []

        for color in instance.colors.all():
            sizes = color.sizes.all()
            color_data = {
                'id': color.id,
                'name': color.name,
                'sizes': [{'id': size.id, 'name': size.name, 'quantity': size.quantity} for size in sizes]
            }
            colors_with_sizes.append(color_data)

        representation['colors'] = colors_with_sizes
        return representation



class ProductDetailSerializer(serializers.ModelSerializer):
    category = serializers.SerializerMethodField()
    variations = serializers.SerializerMethodField()
    images = serializers.SerializerMethodField()  # Use SerializerMethodField to handle images

    class Meta:
        model = Product
        fields = [
            'id', 'product_tag', 'category', 'name', 'slug', 'desc', 
            'price', 'discounted_percentage', 'quantity', 
            'initial_stock_quantity', 'is_suspended', 'created_at', 
            'updated_at', 'variations', 'images'  # Include images field here
        ]

    def get_category(self, obj):
        if obj.category:
            return {
                'id': obj.category.id,
                'super_category': obj.category.super_category.id if obj.category.super_category else None,
                'name': obj.category.name,
                'created_at': obj.category.created_at,
                'updated_at': obj.category.updated_at,
            }
        return None

    def get_variations(self, obj):
        variations = obj.variations.all()  # Assuming you have a related name 'variations' in the Variation model
        return VariationSerializer(variations, many=True).data

    def get_images(self, obj):
        # Access related ProductImage instances through the default related name 'productimage_set'
        return [image.image.url for image in obj.productimage_set.all()]

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        # Add image URLs to the representation
        representation['images'] = self.get_images(instance)
        return representation


 


class ProductSerializer(serializers.ModelSerializer, ImageHandlingMixin):
    variations = VariationSerializer(many=True, required=False)
    category_id = serializers.IntegerField(write_only=True, required=True)
    images = ProductImageSerializer(many=True, read_only=True)  # Directly use ProductImageSerializer for images

    class Meta:
        model = Product
        fields = ['product_tag', 'name', 'slug', 'desc' 'category', 'price', 'quantity', 'initial_stock_quantity', 'is_suspended', 'images']
        extra_kwargs = {
            'slug': {'required': False},
            'category': {'read_only': True},
        }

    def create(self, validated_data):
        variations_data = validated_data.pop('variations', [])
        category_id = validated_data.pop('category_id', None)
        image_files = validated_data.pop('image_files', [])

        if category_id:
            try:
                category = ProductCategory.objects.get(id=category_id)
                validated_data['category'] = category
            except ProductCategory.DoesNotExist:
                raise serializers.ValidationError("Invalid category ID provided.")
        else:
            raise serializers.ValidationError("Category ID is required.")

        name = validated_data.get('name')
        product_tag = validated_data.get('product_tag', 'TS')
        slug = self.generate_unique_slug(name, product_tag)
        validated_data['slug'] = slug

        product = super().create(validated_data)

        # Create ProductImage instances
        for image_file in image_files:
            ProductImage.objects.create(product=product, image=image_file)

        # Create Variation instances
        for variation_data in variations_data:
            variation_data['product_variant'] = product
            Variation.objects.create(**variation_data)

        return product

    def update(self, instance, validated_data):
        image_files = validated_data.pop('image_files', [])

        if image_files:
            # Delete existing images if new ones are provided
            instance.productimage_set.all().delete()

        # Create new ProductImage instances
        for image_file in image_files:
            ProductImage.objects.create(product=instance, image=image_file)

        return super().update(instance, validated_data)

    def generate_unique_slug(self, name, product_tag):
        cleaned_name = name.replace("'", "")
        base_slug = cleaned_name.lower().replace(' ', '-')
        random_chars = ''.join(random.choices(string.ascii_letters + string.digits, k=4))
        slug = f"{base_slug}-{product_tag}-{random_chars}"

        counter = 1
        while Product.objects.filter(slug=slug).exists():
            slug = f"{base_slug}-{product_tag}-{random_chars}-{counter}"
            counter += 1

        return slug

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        # The images field is automatically populated by the ProductImageSerializer
        return representation




class ProductDeleteSerializer(serializers.Serializer):
    product_ids = serializers.ListField(child=serializers.IntegerField())

class CoverPageCarouselSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = CoverPageCarousel
        fields = ['id', 'images', 'image_url']

    def get_image_url(self, obj):
        return obj.images.url if obj.images else None

class LatestArivalSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = LatestArival
        fields = ['id', 'product', 'image', 'image_url']

    def get_image_url(self, obj):
        return obj.image.url if obj.image else None
