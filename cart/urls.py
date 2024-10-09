from django.urls import path
from .background_job import start_background_tasks

# Uncomment this line to start background tasks if needed
# start_background_tasks()

from cart.views import (
    AddToCartView,
    AddWishlistToCartView, 
    CartItemListView,
    PublicWishlistView,
    RemoveFromCartView,
    UpdateCartItemQuantityView,
    WishlistAPIView,
    WishlistView,
)

urlpatterns = [
    path('add-to-cart/', AddToCartView.as_view()),
    path('cart-items/', CartItemListView.as_view()),


    path('cart-items/<int:pk>/remove/', RemoveFromCartView.as_view()),
    path('cart-items/update-quantity/<int:item_id>/', UpdateCartItemQuantityView.as_view()),
    
    path('wishlist/', WishlistAPIView.as_view(), name='wishlist-list-create'),
    path('wishlist/<slug:slug>/', WishlistAPIView.as_view(), name='wishlist-detail-update-delete'),
    
]
