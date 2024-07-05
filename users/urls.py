from django.urls import path, include
from users.views import (
    ActivateUserAPIView,
    AddressCreateView,
    AddressUpdateView,
    AdminLoginView,
    AdminProfileDetail,
    AdminProfileList,
    
    ChangePasswordAPIView,
    CreateAdminAPIView,
    LockAdminUserAPIView,
    LogoutAPIView,
    CreateUserAPIView,
    
    UnlockAdminUserAPIView,
    UserDetailsView,
    UserLoginAPIView,
    UserListView,
    CustomerProfileAPIView,
    
    BillingAddressDetailAPIView,
    ShippingAddressDetailAPIView,

    CustomerProfileListAPIView, 
    DeleteAllProfilesAPIView,
    UserUpdateView,
    
    AdminUserList
)

urlpatterns = [
    path('register/', CreateUserAPIView.as_view() ),
    path('login/', UserLoginAPIView.as_view() ),

    path('admin/login/', AdminLoginView.as_view(), name='admin-login'),
    
    path('activate/<str:activation_token>/', ActivateUserAPIView.as_view() ),
    path('auth/logout/', LogoutAPIView.as_view(), name='logout'),
    path('change_password/', ChangePasswordAPIView.as_view() ),
    path('password_reset/', include('django_rest_passwordreset.urls' )),

    path('admin-profiles/', AdminProfileList.as_view() ),
    path('admin-list/', AdminUserList.as_view() ),
    path('adminprofile/<uuid:uuid>/', AdminProfileDetail.as_view()),
    path('create_admin/', CreateAdminAPIView.as_view() ),
    path('list-users/', UserListView.as_view()),
    
    path('admin/lock/<str:user_id>/', LockAdminUserAPIView.as_view()),
    path('admin/unlock/<str:user_id>/', UnlockAdminUserAPIView.as_view()),
    
    path('customer-profile-details/<str:pk>/', CustomerProfileAPIView.as_view()),
    path('user-update/<uuid:user_id>/', UserUpdateView.as_view(), name='user-update'),

    path('addresses/create/', AddressCreateView.as_view(), name='address-create'),
    path('addresses/update/<int:pk>/', AddressUpdateView.as_view(), name='address-update'),
    path('billing_address_details/', BillingAddressDetailAPIView.as_view(), name='billing-address-detail'),
    path('shipping_address_details/', ShippingAddressDetailAPIView.as_view(), name='shipping-address-detail'),
    
    path('customer_profiles/', CustomerProfileListAPIView.as_view(), name='customer_profiles'),
    path('delete_all_profiles/', DeleteAllProfilesAPIView.as_view(), name='delete_all_profiles'),

    path('active-user-details/', UserDetailsView.as_view()),
]
