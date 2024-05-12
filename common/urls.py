from unicodedata import name
from django.urls import path

from .views import (
        DashboardData,
        RatingCreateView,
        RatingsView
       )
from rest_framework_simplejwt.views import (TokenRefreshView,)

urlpatterns = [
    
        #RATING ROUTES
        path('ratings/create-rating', RatingCreateView.as_view()),
        path('ratings/ratings', RatingsView.as_view()),
        path('dashboard-data/', DashboardData.as_view()),
    
    ]