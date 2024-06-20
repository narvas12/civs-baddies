# urls.py
from django.urls import path
from orders.views import (
    CreateOrderFromCartView,
    OrderCreateAPIView,
    # PaystackWebhook,
    TrendingProducts,
    # Payment
    
)

urlpatterns = [
    path('create-order/', OrderCreateAPIView.as_view()),
    path('session-create-order/', CreateOrderFromCartView.as_view(), name='create-order'),
    # path('pay-for-order/', PaystackWebhook.as_view()),
    path('trending-products/', TrendingProducts.as_view()),
    # path("payment/", Payment),
]

