# urls.py
from django.urls import path
from orders.views import (
    OrderCreateAPIView,
    # PaystackWebhook,
    TrendingProducts,
    UserOrdersView,
    # Payment
    
)

urlpatterns = [
    path('create-order/', OrderCreateAPIView.as_view()),
    # path('pay-for-order/', PaystackWebhook.as_view()),
    path('trending-products/', TrendingProducts.as_view()),
    # path("payment/", Payment),
    path('my_orders/', UserOrdersView().as_view())
]

