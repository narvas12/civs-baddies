from unicodedata import name
from django.urls import path

from .views import (
        DashboardData,
        NewsFlashAPIView,
        RatingCreateView,
        RatingsView
       )
from rest_framework_simplejwt.views import (TokenRefreshView,)

urlpatterns = [
    
        path('ratings/create-rating', RatingCreateView.as_view()),
        path('ratings/ratings', RatingsView.as_view()),
        path('dashboard-data/', DashboardData.as_view()),
        path('newsflash/', NewsFlashAPIView.as_view()),              # For list and create
        path('newsflash/<int:newsflash_id>/', NewsFlashAPIView.as_view())
    ]