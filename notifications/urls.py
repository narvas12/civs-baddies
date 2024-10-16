from django.urls import path
from .views import NewsFlashAPIView

urlpatterns = [
    path('newsflash/', NewsFlashAPIView.as_view(), name='newsflash-list-create'),
    path('newsflash/<int:pk>/', NewsFlashAPIView.as_view(), name='newsflash-detail'),
]
