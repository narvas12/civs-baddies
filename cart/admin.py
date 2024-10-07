from django.contrib import admin

from cart.models import CartItem, WishlistItem

@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display =['id','user', 'product', 'quantity']


@admin.register(WishlistItem)
class WishListItemAdmin(admin.ModelAdmin):
    list_display = ['product']