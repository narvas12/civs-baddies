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
    SessionId,
)

urlpatterns = [
    path('add-to-cart/', AddToCartView.as_view(), name='add_to_cart'),
    path('cart-items/', CartItemListView.as_view(), name='cart_items'),
    path('cart-items/<int:pk>/remove/', RemoveFromCartView.as_view(), name='remove_from_cart'),
    path('cart-items/update-quantity/<int:item_id>/', UpdateCartItemQuantityView.as_view(), name='update_cart_item_quantity'),
    
    path('wishlist/add/', AddToWishlistView.as_view(), name='add_to_wishlist'),
    path('wishlist/add-to-cart/', AddWishlistToCartView.as_view(), name='add_wishlist_to_cart'),
    path('wishlist/', WishlistView.as_view(), name='wishlist'),
    path('wishlist/public/<str:unique_identifier>/', PublicWishlistView.as_view(), name='public_wishlist'),
    
    path('session-id/', SessionId.as_view(), name='session_id'),
]
