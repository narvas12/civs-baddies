from django.urls import path
from .background_job import start_background_tasks

# Uncomment this line to start background tasks if needed
# start_background_tasks()

from cart.views import (
    AddToCartView,
    AddToWishlistView,
    AddWishlistToCartView, 
    CartItemListView,
    PublicWishlistView,
    RemoveFromCartView,
    UpdateCartItemQuantityView,
    WishlistView,
)

urlpatterns = [
    path('add-to-cart/', AddToCartView.as_view()),
    path('cart-items/', CartItemListView.as_view()),


    path('cart-items/<int:pk>/remove/', RemoveFromCartView.as_view()),
    path('cart-items/update-quantity/<int:item_id>/', UpdateCartItemQuantityView.as_view()),
    
    path('wishlist/add/', AddToWishlistView.as_view()),
    path('wishlist/add-to-cart/', AddWishlistToCartView.as_view()),
    path('wishlist/', WishlistView.as_view()),
    path('wishlist/public/<str:unique_identifier>/', PublicWishlistView.as_view()),
    
]
