import uuid
from venv import logger
from django.db import IntegrityError
from django.shortcuts import get_object_or_404
from rest_framework import serializers
from core import settings
from users.utils import send_activation_email
from .models import Address, CustomUser, CustomerProfile, AdminProfile
from django_countries.serializers import CountryFieldMixin
import cloudinary
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken, TokenError
from django.core.validators import FileExtensionValidator
from rest_framework.exceptions import AuthenticationFailed
from django.contrib.auth import get_user_model, authenticate
from django.core.validators import RegexValidator
from rest_framework import serializers
cloudinary.config(
            cloud_name=settings.CLOUDINARY_STORAGE['CLOUD_NAME'],
            api_key=settings.CLOUDINARY_STORAGE['API_KEY'],
            api_secret=settings.CLOUDINARY_STORAGE['API_SECRET']
        )




class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        exclude = (
            'is_superuser',
            'is_active',
            'activation_token',
            'groups',
            'user_permissions',
            'password',
            'last_login',
        )

class CreateUserSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(max_length=100, required=True)
    email = serializers.EmailField(max_length=255, required=True)
    mobile = serializers.CharField(max_length=15, required=True, validators=[
        RegexValidator(regex=r'^\d{10,15}$', message="Enter a valid mobile number.")
    ])

    class Meta:
        model = CustomUser
        fields = ['full_name', 'email', 'mobile', 'password']
        extra_kwargs = {
            'password': {'write_only': True},
            'email': {'required': True, 'unique': True},
        }

    def create(self, validated_data):
        validated_data['username'] = validated_data['email']  # Set username to email

        try:
            user = CustomUser.objects.create_user(**validated_data)
            user.activation_token = str(uuid.uuid4())
            user.save()
            send_activation_email(user)
            return user
        except IntegrityError as e:
            if 'users_customuser_username_key' in str(e):  
                raise serializers.ValidationError({"email": "This email is already in use."})
            elif 'users_customuser_mobile_key' in str(e):  
                raise serializers.ValidationError({"mobile": "This mobile number is already in use."})
            else:
                raise serializers.ValidationError({"non_field_errors": "A database error occurred."})
        except ValueError as e:

            raise serializers.ValidationError({"non_field_errors": str(e)})
        except Exception as e:

            logger.exception("Error creating user:", exc_info=e)
            raise serializers.ValidationError({"non_field_errors": "An unexpected error occurred."})

           
           


class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ('full_name', 'mobile')  
        extra_kwargs = {'mobile': {'validators': [RegexValidator(regex=r"^\d{10,15}$", message="Enter a valid mobile number")]}}
        read_only_fields = ('email',)  

class UserMiniSerializer(serializers.ModelSerializer):
    profile_picture = serializers.ImageField(source="profile.avatar")
    gender = serializers.CharField(source="profile.gender")
    email = serializers.EmailField(source="profile.gender")


    class Meta:
        model = get_user_model()
        fields = ["username", "avatar", "gender", "email"]



class CreateAdminSerializer(serializers.ModelSerializer):
    password = serializers.CharField(max_length=128, write_only=True)

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'mobile', 'password', 'is_staff', 'is_superuser', 'is_active']
        extra_kwargs = {
            'username': {'required': True},
            'mobile': {'required': True},
            'is_staff':{'required': True},
            'is_superuser':{'required': True},
            'is_active':{'required': True}
        }

    def create(self, validated_data):
        password = validated_data.pop('password')
        is_staff = validated_data.pop('is_staff')
        is_active = validated_data.pop('is_active')
        is_superuser = validated_data.pop('is_superuser')

        user = CustomUser.objects.create_user(is_staff=is_staff, is_active=is_active,is_superuser=is_superuser, **validated_data)
        user.set_password(password)
        user.save()

        return user
    

class AdminLoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()

    def validate(self, data):
        username = data.get('username')
        password = data.get('password')

        if username and password:
            user = authenticate(username=username, password=password)
            if user:
                if not user.is_active:
                    raise serializers.ValidationError('User is disabled.')
                if not user.is_staff:
                    raise serializers.ValidationError('User is not an admin.')
                return user
            else:
                raise serializers.ValidationError('Invalid credentials.')
        else:
            raise serializers.ValidationError('Must include "username" and "password".')

        
class LoginSerializer(serializers.ModelSerializer):
    username = serializers.EmailField(max_length=155, min_length=6)
    password = serializers.CharField(max_length=68, write_only=True)
    full_name = serializers.CharField(max_length=255, read_only=True)
    access_token = serializers.CharField(max_length=255, read_only=True)
    refresh_token = serializers.CharField(max_length=255, read_only=True)
    is_staff = serializers.BooleanField(read_only=True)  # Added field for staff status

    class Meta:
        model = CustomUser
        fields = ['username', 'password', 'full_name', 'access_token', 'refresh_token', 'is_staff']

    def validate(self, attrs):
        username = attrs.get('username')
        password = attrs.get('password')
        request = self.context.get('request')
        user = authenticate(request, username=username, password=password)
        if not user:
            raise AuthenticationFailed("Invalid credentials. Please try again.")
        
        # Check if the user is staff
        is_staff = user.is_staff

        tokens = user.tokens()
        return {
            'username': user.username,
            'full_name': user.get_full_name,
            "access_token": str(tokens.get('access')),
            "refresh_token": str(tokens.get('refresh')),
            "is_staff": is_staff,  # Include staff status in the response
        }
        
        
        
        
class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField()

    def validate(self, attrs):
        self.token = attrs['refresh']
        return attrs

    def save(self, **kwargs):
        from rest_framework_simplejwt.tokens import RefreshToken

        try:
            refresh_token = RefreshToken(self.token)
            refresh_token.blacklist()
        except Exception as e:
            self.fail('bad_token')
           
           
class ChangePasswordSerializer(serializers.Serializer):
    user_id = serializers.UUIDField(required=True)
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)

class ResetPasswordEmailSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    


    
    
class GetAllUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'email', 'customer_id', 'full_name', 'mobile', 'created_at', 'updated_at', 'is_staff', 'is_superuser']




class CustomerProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomerProfile
        fields = ['id', 'user', 'address']



class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = [
            'id',
            'address_type',
            'default',
            'country',
            'city',
            'street_address',
            'apartment_address',
            'postal_code',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['user', 'created_at', 'updated_at']
        

class AdminProfileSerializer(serializers.ModelSerializer):
    avatar = serializers.ImageField(
        max_length=None,
        allow_empty_file=True,
        use_url=True,
        validators=[FileExtensionValidator(allowed_extensions=['png', 'jpg', 'jpeg'])],
        required=False,
    )

    class Meta:
        model = AdminProfile
        fields = "__all__"

    def create(self, validated_data):
        avatar_file = validated_data.pop('avatar', None)
        profile = super().create(validated_data)
        if avatar_file:
            # Upload the avatar to Cloudinary
            upload_result = cloudinary.uploader.upload(avatar_file)
            profile.avatar = upload_result['secure_url']
            profile.save()
        return profile

    def update(self, instance, validated_data):
        avatar_file = validated_data.pop('avatar', None)
        instance = super().update(instance, validated_data)
        if avatar_file:
            # Upload the new avatar and potentially delete the old one (implement logic)
            upload_result = cloudinary.uploader.upload(avatar_file)
            instance.avatar = upload_result['secure_url']
        else:
            # If avatar is not provided, keep the existing one
            instance.avatar = instance.avatar
        instance.save()
        return instance


