# urls.py
from django.urls import path
from orders.views import (
    OrderCreateAPIView,
    OrderDetailView,
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
    path('my_orders/', UserOrdersView().as_view()),
    path('my_order/detail/<int:order_id>/', OrderDetailView.as_view(), name='order-detail'),
]

