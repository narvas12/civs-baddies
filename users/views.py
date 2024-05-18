from django.apps import apps
from django.conf import settings
from django.http import HttpResponseNotFound
from django.shortcuts import get_object_or_404, redirect
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.generics import CreateAPIView, UpdateAPIView, GenericAPIView
from rest_framework import status, generics
from rest_framework.pagination import PageNumberPagination
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.exceptions import NotFound
from django.contrib.auth import authenticate, update_session_auth_hash
from rest_framework.permissions import IsAuthenticated
from common.pagination import CustomPagination
from rest_framework import viewsets
from rest_framework_simplejwt.tokens import RefreshToken
from users.models import CustomUser, CustomerProfile, AdminProfile, Address
from django.contrib.auth.hashers import make_password
from users.permissions import IsSuperUser, IsUserProfileOwner
from django.db import IntegrityError
from .serializers import (
    AddressSerializer,
    AdminLoginSerializer,
    # BillingAddressSerializer,
    CreateAdminSerializer,
    ChangePasswordSerializer,
    CreateUserSerializer,
    CustomUserSerializer,
    CustomerProfileSerializer,
    LoginSerializer,
    LogoutUserSerializer,
    AdminProfileSerializer,
    # ShippingAddressSerializer,
    GetAllUserSerializer,
    UserUpdateSerializer,
)

class BaseAPIView(APIView):
    pagination_class = None
    serializer_class = None

    def get_serializer_class(self):
        assert self.serializer_class is not None, (
            "'%s' should either include a `serializer_class` attribute, "
            "or override the `get_serializer_class()` method."
            % self.__class__.__name__
        )
        return self.serializer_class

    def get_paginated_response(self, data):
        if self.pagination_class:
            paginator = self.pagination_class()
            page = paginator.paginate_queryset(data, self.request)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                return paginator.get_paginated_response(serializer.data)
        return Response(data)



class UserListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]

    serializer_class = GetAllUserSerializer
    pagination_class = CustomPagination

    def get_queryset(self):
        return CustomUser.objects.filter(is_staff=False)

        

class CreateUserAPIView(APIView):
    def post(self, request):
        serializer = CreateUserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'User created successfully. Check your email for activation.'}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class UserUpdateView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, user_id):
        user = get_object_or_404(CustomUser, id=user_id)
        
        # # Ensure the user performing the update is the same as the user being updated
        # if request.user.id != user.id:
        #     return Response({"detail": "You do not have permission to perform this action."}, status=status.HTTP_403_FORBIDDEN)

        serializer = UserUpdateSerializer(user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data)
    
    
class ActivateUserAPIView(APIView):
    def get(self, request, activation_token, *args, **kwargs):
        try:
            user = CustomUser.objects.get(activation_token=activation_token)
            user.is_active = True
            user.activation_token = None
            user.save()
            return redirect(settings.LOGIN_REDIRECT_URL) 
        except CustomUser.DoesNotExist:
            return Response({"detail": "Activation link is invalid."}, status=status.HTTP_404_NOT_FOUND)

        
class UserLoginAPIView(GenericAPIView):
    serializer_class=LoginSerializer
    
    def post(self, request):
        serializer= self.serializer_class(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data, status=status.HTTP_200_OK)




class LogoutApiView(GenericAPIView):
    serializer_class=LogoutUserSerializer
    # renderer_classes = (ApiCustomRenderer,)

    def post(self, request):
        serializer=self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'message':"Logout is succesful"}, status=status.HTTP_200_OK)


class ChangePasswordAPIView(BaseAPIView):
    # permission_classes = [IsAuthenticated]
    serializer_class = ChangePasswordSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            user_id = serializer.validated_data.get('user_id')
            old_password = serializer.validated_data.get('old_password')
            new_password = serializer.validated_data.get('new_password')

            try:
                user = CustomUser.objects.get(id=user_id)
            except CustomUser.DoesNotExist:
                return Response({'error': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)

            if user.check_password(old_password):
                user.set_password(new_password)
                user.save()
                update_session_auth_hash(request, user)  # To update session after password change
                return Response({'message': 'Password changed successfully.'}, status=status.HTTP_200_OK)
            else:
                return Response({'error': 'Incorrect old password.'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)




class CreateAdminAPIView(APIView):
    # permission_classes = [IsSuperUser]
    
    def post(self, request):
        serializer = CreateAdminSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'Admin user created successfully.'}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class AdminLoginView(generics.GenericAPIView):
    serializer_class = AdminLoginSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data

        refresh = RefreshToken.for_user(user)
        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }, status=status.HTTP_200_OK)
    

class AdminProfileDetail(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    queryset = AdminProfile.objects.all()
    serializer_class = AdminProfileSerializer

    def get(self, request, uuid):  # Use 'uuid' in the URL
        try:
            user_profile = self.queryset.get(user__id=uuid)  # Filter by user__id
            serializer = self.serializer_class(user_profile)
            return Response(serializer.data)
        except AdminProfile.DoesNotExist:
            return Response({"message": "Profile not found"}, status=status.HTTP_404_NOT_FOUND)

    def put(self, request, uuid):  # Use 'uuid' in the URL
        try:
            user_profile = self.queryset.get(user__id=uuid)  # Filter by user__id
            serializer = self.serializer_class(user_profile, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except AdminProfile.DoesNotExist:
            return Response({"message": "Profile not found"}, status=status.HTTP_404_NOT_FOUND)
    


class AdminProfileList(generics.ListAPIView):
    queryset = AdminProfile.objects.all()
    serializer_class = AdminProfileSerializer



class LockAdminUserAPIView(APIView):
    permission_classes = [IsSuperUser]

    def post(self, request, user_id):
        try:
            user = CustomUser.objects.get(id=user_id)
            user.password = make_password(None)  
            user.save()
            
            return Response({'message': f'Admin user {user.username} locked successfully.'}, status=status.HTTP_200_OK)
        except ObjectDoesNotExist:
            return Response({'error': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)


class UnlockAdminUserAPIView(APIView):
    permission_classes = [IsSuperUser]

    def post(self, request, user_id):
        try:
            user = CustomUser.objects.get(id=user_id)
            user.set_password('P@sword.123')  
            user.save()

            return Response({'message': f'Admin user {user.username} unlocked successfully.'}, status=status.HTTP_200_OK)
        except ObjectDoesNotExist:
            return Response({'error': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)


class AdminUserList(generics.ListAPIView):
    # permission_classes = [IsSuperUser]

    serializer_class = GetAllUserSerializer
    pagination_class = CustomPagination

    def get_queryset(self):
        return CustomUser.objects.filter(is_staff=True)

    
class DeactivateStaffUserAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        try:
            user = CustomUser.objects.get(pk=pk, is_staff=True)
            user.is_active = False
            user.save()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except CustomUser.DoesNotExist:
            return Response({'error': 'User not found or is not staff'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



class CustomerProfileAPIView(APIView):
    def get(self, request, pk):
        try:
            profile = CustomerProfile.objects.get(id=pk)
            serializer = CustomerProfileSerializer(profile)
            return Response(serializer.data)
        except CustomerProfile.DoesNotExist:
            return Response({"error": "Customer Profile not found"}, status=status.HTTP_404_NOT_FOUND)


class CustomerProfileListAPIView(APIView):
    def get(self, request):
        customers = CustomUser.objects.filter(is_staff=False, is_superuser=False)
        serialized_customers = CustomUserSerializer(customers, many=True)
        return Response(serialized_customers.data)


class AddressCreateView(CreateAPIView):
    serializer_class = AddressSerializer

    def get_queryset(self):
        customer_id = self.kwargs['customer_id']
        if customer_id != self.request.user.customer_id:
            raise NotFound('You can only create addresses for yourself')
        return Address.objects.filter(user__customer_id=customer_id)


class AddressUpdateView(UpdateAPIView):
    serializer_class = AddressSerializer

    def get_queryset(self):
        customer_id = self.kwargs['customer_id']
        if customer_id != self.request.user.customer_id:
            raise NotFound('You can only update your own addresses')
        return Address.objects.filter(user__customer_id=customer_id)

    def get_object(self):
        queryset = self.get_queryset()
        obj_id = self.kwargs['pk']
        try:
            return queryset.get(pk=obj_id)
        except Address.DoesNotExist:
            raise NotFound('Address not found')


class BillingAddressDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = AddressSerializer

    def get_object(self):
        customer_id = self.kwargs.get('customer_id')
        queryset = Address.objects.filter(user__customer_id=customer_id, address_type=Address.BILLING)
        return get_object_or_404(queryset)


class ShippingAddressDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = AddressSerializer

    def get_object(self):
        customer_id = self.kwargs.get('customer_id')
        queryset = Address.objects.filter(user__customer_id=customer_id, address_type=Address.SHIPPING)
        return get_object_or_404(queryset)

    


class DeleteAllProfilesAPIView(APIView):
    def delete(self, request):
        CustomUser.objects.all().delete()
        CustomerProfile.objects.all().delete()
        AdminProfile.objects.all().delete()
        return Response({'message': 'All profiles deleted successfully.'}, status=status.HTTP_204_NO_CONTENT)