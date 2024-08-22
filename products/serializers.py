from rest_framework import serializers
from .models import CoverPageCarousel, LatestArival, Product, ProductCategory, Supercategory, Variation, get_default_product_category
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



class VariationSerializer(serializers.ModelSerializer, ImageHandlingMixin):
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = Variation
        fields = '__all__'
        extra_kwargs = {
            'product_variant': {'required': False},
            'image': {'write_only': True},
        }

    def get_image_url(self, obj):
        return obj.image.url if obj.image else None

    def create(self, validated_data):
        if 'image' in validated_data:
            validated_data['image'] = self.upload_image(validated_data['image'])
        return super().create(validated_data)


class CreateVariationsSerializer(serializers.Serializer):
    product_id = serializers.IntegerField()
    variations = VariationSerializer(many=True)

    def create(self, validated_data):
        product_id = validated_data['product_id']
        variations_data = validated_data['variations']
        product = Product.objects.get(id=product_id)
        variations = []

        for variation_data in variations_data:
            variation_data['product_variant'] = product
            variation = Variation.objects.create(**variation_data)
            variations.append(variation)

        return variations


class ProductDetailSerializer(serializers.ModelSerializer):
    category = serializers.SerializerMethodField()
    name = serializers.CharField()
    variations = serializers.SerializerMethodField()
    image_url = serializers.SerializerMethodField()

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
        variations = obj.variations.all()
        return VariationSerializer(variations, many=True).data

    def get_image_url(self, obj):
        return obj.image.url if obj.image else None

    class Meta:
        model = Product
        fields = [
            'id','product_tag', 'category', 'name', 'slug', 'desc', 
            'image_url', 'price', 'discounted_percentage', 'quantity', 
            'initial_stock_quantity', 'is_suspended', 'created_at', 
            'updated_at', 'variations'
        ]



class ProductSerializer(serializers.ModelSerializer, ImageHandlingMixin):
    variations = VariationSerializer(many=True, required=False)
    category_id = serializers.IntegerField(write_only=True, required=True)
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = '__all__'
        extra_kwargs = {
            'slug': {'required': False},
            'category': {'read_only': True},
            'image': {'write_only': True},
        }

    def create(self, validated_data):
        variations_data = validated_data.pop('variations', [])
        category_id = validated_data.pop('category_id', None)

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

        if 'image' in validated_data:
            validated_data['image'] = self.upload_image(validated_data['image'])

        product = super().create(validated_data)

        for variation_data in variations_data:
            variation_data['product_variant'] = product
            Variation.objects.create(**variation_data)

        return product

    def get_image_url(self, obj):
        return obj.image.url if obj.image else None

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


# class ProductDetailSerializer(serializers.ModelSerializer):
#     category = ProductCategorySerializer()
#     class Meta:
#         model = Product
#         fields = [
#             'product_tag', 'category', 'name', 'slug', 'desc', 
#             'image', 'price', 'discounted_percentage', 'quantity', 
#             'initial_stock_quantity', 'is_suspended', 'created_at', 'updated_at'
#         ]

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
