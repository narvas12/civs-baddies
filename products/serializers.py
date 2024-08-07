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


class ProductDetailSerializer(serializers.ModelSerializer):
   
    category = ProductCategorySerializer(read_only=True)
    name = serializers.CharField()
    image = Base64ImageField()

    def get_category(self, obj):
        return obj.category.name

    class Meta:
        model = Product
        exclude = "modified"


class VariationSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = Variation
        fields = '__all__'
        extra_kwargs = {
            'product_variant': {'required': False},
            'image': {'write_only': True},
        }

    def get_image_url(self, obj):
        # Return the Cloudinary URL of the uploaded image
        return obj.image.url if obj.image else None


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
    

class ProductSerializer(serializers.ModelSerializer):
    variations = VariationSerializer(many=True, required=False)
    category = ProductCategorySerializer(read_only=True)

    class Meta:
        model = Product
        fields = '__all__'
        extra_kwargs = {
            'slug': {'required': False},
            'category': {'required': False}
        }

    def create(self, validated_data):
        variations_data = validated_data.pop('variations', [])
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
    

    def upload_image(self, image):
        cloudinary.config(
            cloud_name=settings.CLOUDINARY_STORAGE['CLOUD_NAME'],
            api_key=settings.CLOUDINARY_STORAGE['API_KEY'],
            api_secret=settings.CLOUDINARY_STORAGE['API_SECRET']
        )

        upload_result = upload(image, folder="product/images/")
        return upload_result['secure_url']


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