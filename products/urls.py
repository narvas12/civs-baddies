from django.urls import path


from .views import (
                    CoverPageCarouselAPIView,
                    CoverPageCarouselListView,
                    LatestArivalAPIView,
                    CategoryCreateAPIView,
                    LatestArrivalListView,
                    ProductAPIView,
                    ProductCategoryListAPIView,
                    ProductImageListView,
                    SuperCategoryCreateAPIView,
                    VariationAPIView,
                    )



urlpatterns = [
    path('product/', ProductAPIView.as_view()),
    path('product/<int:pk>/', ProductAPIView.as_view()),

    path('super-categories/add/', SuperCategoryCreateAPIView.as_view()),

    path('categories/add/', CategoryCreateAPIView.as_view()),
    path('categories/list/', ProductCategoryListAPIView.as_view()),

    path('variations/', VariationAPIView.as_view()),
    path('variations/<int:pk>/', VariationAPIView.as_view()),


    path('coverpage-carousel/add/', CoverPageCarouselAPIView.as_view()),
    path('cover-page-carousels/', CoverPageCarouselListView.as_view()),

    path('latest-arrivals/add/', LatestArivalAPIView.as_view()),
    path('latest-arrivals/', LatestArrivalListView.as_view()),

    path('product-images/', ProductImageListView.as_view()),

]

