from django.contrib import admin

from users.models import CustomUser, CustomerProfile, LoginLog, UserVisit, AdminProfile, Address

# Register your models here.
@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ['id', 'customer_id','email', 'created_at', 'is_active', 'is_staff']
    
    
    
@admin.register(UserVisit)
class UserVisitAdmin(admin.ModelAdmin):
    list_display = ('user', 'timestamp', 'remote_addr', 'browser', 'device', 'os')


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    
    list_display = ['id','user', 'address_type', 'country']
    
    
@admin.register(AdminProfile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ['user']
    
@admin.register(CustomerProfile)
class CustomerProfileAdmin(admin.ModelAdmin):
    list_display = ['id','user']
    
    
@admin.register(LoginLog)
class LoginLogAdmin(admin.ModelAdmin):
    list_display = ['user', 'login_time', 'login_failed', 'logout_time', 'login_location']