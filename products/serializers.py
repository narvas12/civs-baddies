from rest_framework import serializers
from .models import Product, ProductCategory, Variation, get_default_product_category
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


class ProductDetailSerializer(serializers.ModelSerializer):
   
    category = serializers.SerializerMethodField()
    name = serializers.CharField()
    image = Base64ImageField()

    def get_category(self, obj):
        return obj.category.name

    class Meta:
        model = Product
        exclude = "modified"


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'
        extra_kwargs = {
            'slug': {'required': False},
            'category': {'required': False}
        }

    def create(self, validated_data):
        name = validated_data.get('name')
        product_tag = validated_data.get('product_tag', 'TS')  # Default product tag
        slug = self.generate_unique_slug(name, product_tag)
        validated_data['slug'] = slug

        # Upload image to Cloudinary if present in request data
        if 'image' in validated_data:
            validated_data['image'] = self.upload_image(validated_data['image'])

        return super().create(validated_data)

    def generate_unique_slug(self, name, product_tag):
        

        # Remove single quotes from the product name
        cleaned_name = name.replace("'", "")

        base_slug = cleaned_name.lower().replace(' ', '-')
        random_chars = ''.join(random.choices(string.ascii_letters + string.digits, k=4))
        slug = f"{base_slug}-{product_tag}-{random_chars}"
        
        # Ensure slug is unique
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
        # Upload image to Cloudinary
        upload_result = upload(image, folder="product/images/")
        return upload_result['secure_url']



# class VariationSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Variation
#         fields = '__all__'

#     def create(self, validated_data):
#         return super().create(validated_data)

#     def update(self, instance, validated_data):
#         return super().update(instance, validated_data)
    


class VariationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Variation
        fields = '__all__'




class ProductDeleteSerializer(serializers.Serializer):
    product_ids = serializers.ListField(child=serializers.IntegerField())
