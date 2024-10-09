from django.contrib import admin

from cart.models import CartItem, WishList

@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display =['id','user', 'product', 'quantity']


@admin.register(WishList)
class WishListItemAdmin(admin.ModelAdmin):
    list_display = ['display_products']

    def display_products(self, obj):
        return ", ".join([str(product) for product in obj.product.all()])
    display_products.short_description = 'Products'