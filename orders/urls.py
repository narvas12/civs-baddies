# urls.py
from django.urls import path
from orders.views import (
    AdminOrderDetailView,
    OrderCreateAPIView,
    OrderDetailView,
    OrderItemsListView,
    OrderListView,
    OrderStatusUpdateView,
    PaymentAPIView,
    TrendingProducts,
    UserOrdersView,
    paystack_webhook,
)

urlpatterns = [
    path('create-order/', OrderCreateAPIView.as_view()),

    path('payment/<int:order_id>/pay/', PaymentAPIView.as_view()),
    path('payment/<int:order_id>/callback/', PaymentAPIView.as_view()),
    
    path('trending-products/', TrendingProducts.as_view()),
    path('my_orders/', UserOrdersView().as_view()),
    path('orders/', OrderListView.as_view()),
    path('my_order/detail/<int:order_id>/', OrderDetailView.as_view()),
    path('orders/<int:order_id>/items/', OrderItemsListView.as_view()),
    path('orders/admin_details/<int:id>/', AdminOrderDetailView.as_view()),
    path('orders/<int:id>/status/update/', OrderStatusUpdateView.as_view()),
    path('paystack-webhook/', paystack_webhook, name='paystack-webhook'),
]

