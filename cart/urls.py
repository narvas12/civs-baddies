# urls.py
from django.urls import path
from .background_job import start_background_tasks


# start_background_tasks()

from cart.views import (
    AddToCartView,
    AddToWishlistView,
    AddWishlistToCartView, 
    CartItemListView,
    # DeleteCartItems,
    PublicWishlistView,
    RemoveFromCartView,
    UpdateCartItemQuantityView,
    WishlistView
    
)



urlpatterns = [
    path('add-to-cart/', AddToCartView.as_view()),
    path('cart-items/<str:customer_id>/', CartItemListView.as_view()),
    path('cart-items/<int:pk>/remove/', RemoveFromCartView.as_view()),
    path('cart_items/<str:customer_id>/update-quantity/<int:item_id>/', UpdateCartItemQuantityView.as_view()),

    # path('delete_cart/', DeleteCartItems.as_view()),
    path('wishlist/add/', AddToWishlistView.as_view()),
    path('wishlist/add-to-cart/', AddWishlistToCartView.as_view()),
    path('wishlist/<str:customer_id>/', WishlistView.as_view()),

    path('wishlist/<str:unique_identifier>/', PublicWishlistView.as_view()),
]
