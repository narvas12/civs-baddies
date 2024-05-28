from rest_framework import serializers
from .models import CoverPageCarousel, LatestArival, Product, ProductCategory, Variation, get_default_product_category
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



# class ProductSerializer(serializers.ModelSerializer):
#     images = serializers.ListField(
#         child=serializers.ImageField(), write_only=True, required=False
#     )
#     featured_image = serializers.ImageField(write_only=True, required=False)

#     class Meta:
#         model = Product
#         fields = '__all__'
#         extra_kwargs = {
#             'slug': {'required': False},
#             'category': {'required': False}
#         }

#     def create(self, validated_data):
#         name = validated_data.get('name')
#         product_tag = validated_data.get('product_tag', 'TS')
#         slug = self.generate_unique_slug(name, product_tag)
#         validated_data['slug'] = slug

#         if 'images' in validated_data:
#             validated_data['images'] = self.upload_images(validated_data.pop('images'))

#         if 'featured_image' in validated_data:
#             validated_data['featured_image'] = self.upload_image(validated_data.pop('featured_image'))

#         return super().create(validated_data)

#     def update(self, instance, validated_data):
#         if 'images' in validated_data:
#             validated_data['images'] = self.upload_images(validated_data.pop('images'))

#         if 'featured_image' in validated_data:
#             validated_data['featured_image'] = self.upload_image(validated_data.pop('featured_image'))

#         return super().update(instance, validated_data)

#     def generate_unique_slug(self, name, product_tag):
#         cleaned_name = name.replace("'", "")
#         base_slug = cleaned_name.lower().replace(' ', '-')
#         random_chars = ''.join(random.choices(string.ascii_letters + string.digits, k=4))
#         slug = f"{base_slug}-{product_tag}-{random_chars}"

#         counter = 1
#         while Product.objects.filter(slug=slug).exists():
#             slug = f"{base_slug}-{product_tag}-{random_chars}-{counter}"
#             counter += 1

#         return slug

#     def upload_images(self, images):
#         cloudinary.config(
#             cloud_name=settings.CLOUDINARY_STORAGE['CLOUD_NAME'],
#             api_key=settings.CLOUDINARY_STORAGE['API_KEY'],
#             api_secret=settings.CLOUDINARY_STORAGE['API_SECRET']
#         )
#         image_urls = []
#         for image in images:
#             upload_result = upload(image, folder="product/images/")
#             image_urls.append(upload_result['secure_url'])
#         return image_urls

#     def upload_image(self, image):
#         cloudinary.config(
#             cloud_name=settings.CLOUDINARY_STORAGE['CLOUD_NAME'],
#             api_key=settings.CLOUDINARY_STORAGE['API_KEY'],
#             api_secret=settings.CLOUDINARY_STORAGE['API_SECRET']
#         )
#         upload_result = upload(image, folder="product/featured_image/")
#         return upload_result['secure_url']

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
        product_tag = validated_data.get('product_tag', 'TS') 
        slug = self.generate_unique_slug(name, product_tag)
        validated_data['slug'] = slug

        if 'image' in validated_data:
            validated_data['image'] = self.upload_image(validated_data['image'])

        return super().create(validated_data)

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



class VariationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Variation
        fields = '__all__'

    def create(self, validated_data):
        return super().create(validated_data)

    def update(self, instance, validated_data):
        return super().update(instance, validated_data)
    


class VariationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Variation
        fields = '__all__'



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