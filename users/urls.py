from django.urls import path, include
from users.views import (
    ActivateUserAPIView,
    AddressCreateView,
    AddressUpdateView,
    AdminProfileDetail,
    AdminProfileList,
    
    ChangePasswordAPIView,
    CreateAdminAPIView,
    LockAdminUserAPIView,
    LogoutApiView,
    CreateUserAPIView,
    
    UnlockAdminUserAPIView,
    UserLoginAPIView,
    UserListView,
    CustomerProfileAPIView,
    
    BillingAddressDetailAPIView,
    ShippingAddressDetailAPIView,

    CustomerProfileListAPIView, 
    DeleteAllProfilesAPIView,
    UserUpdateView
  
)

urlpatterns = [
    path('register/', CreateUserAPIView.as_view() ),
    path('login/', UserLoginAPIView.as_view() ),
    path('activate/<str:activation_token>/', ActivateUserAPIView.as_view() ),
    path('auth/logout', LogoutApiView.as_view(), name='logout'),
    path('change_password/', ChangePasswordAPIView.as_view() ),
    path('password_reset/', include('django_rest_passwordreset.urls' )),

    path('admin-profiles/', AdminProfileList.as_view() ),
    path('adminprofile/<uuid:uuid>/', AdminProfileDetail.as_view()),
    path('create_admin/', CreateAdminAPIView.as_view() ),
    path('list-users/', UserListView.as_view()),
    
    path('admin/lock/<str:user_id>/', LockAdminUserAPIView.as_view()),
    path('admin/unlock/<str:user_id>/', UnlockAdminUserAPIView.as_view()),
    
    path('customer-profile-details/<str:pk>/', CustomerProfileAPIView.as_view()),
    path('user-update/<uuid:user_id>/', UserUpdateView.as_view(), name='user-update'),

    path('addresses/<str:customer_id>/', AddressCreateView.as_view()),
    path('addresses/<str:customer_id>/<int:pk>/', AddressUpdateView.as_view()),
    path('billing_address_details/<str:customer_id>/', BillingAddressDetailAPIView.as_view()),
    path('shipping_address_details/<str:customer_id>/', ShippingAddressDetailAPIView.as_view()),
    
    path('customer_profiles/', CustomerProfileListAPIView.as_view(), name='customer_profiles'),
    path('delete_all_profiles/', DeleteAllProfilesAPIView.as_view(), name='delete_all_profiles'),
]
