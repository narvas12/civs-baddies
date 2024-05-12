from django.urls import path
from .views import (

    CheckoutCartView
)


urlpatterns = [
       path('checkout/cart/<str:customer_id>/<int:pk>/', CheckoutCartView.as_view()),
]
