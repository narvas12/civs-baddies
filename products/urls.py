from django.urls import path


from .views import (
                    
                   
                    CoverPageCarouselAPIView,
                    CoverPageCarouselListView,
                    CreateVariationsView,
                    LatestArivalAPIView,
                    CategoryCreateAPIView,
                    LatestArrivalListView,
                    ProductAPIView,
                    ProductCategoryListAPIView,
                    
                    SuperCategoryCreateAPIView,
                    
                    VariationCreateView,
                    VariationListCreateAPIView,
                    VariationRetrieveUpdateDestroyAPIView,
                    VariationListAPIView,
                    )



urlpatterns = [
    path('product/', ProductAPIView.as_view(), name='product-list-create'),
    path('product/<int:pk>/', ProductAPIView.as_view(), name='product-detail-update-destroy'),

    path('super-categories/add/', SuperCategoryCreateAPIView.as_view()),

    path('categories/add/', CategoryCreateAPIView.as_view()),
    path('categories/list/', ProductCategoryListAPIView.as_view()),

    path('variations/', VariationListAPIView.as_view()),
    path('variations/create/', CreateVariationsView.as_view()), #add multiple variations for a product
    path('variations/add/', VariationCreateView.as_view()), #add single variation
    path('variations/<int:pk>/', VariationRetrieveUpdateDestroyAPIView.as_view()),
    path('variations/product/<int:product_id>/', VariationListCreateAPIView.as_view()),


    path('coverpage-carousel/add/', CoverPageCarouselAPIView.as_view()),
    path('cover-page-carousels/', CoverPageCarouselListView.as_view()),

    path('latest-arrivals/add/', LatestArivalAPIView.as_view()),
    path('latest-arrivals/', LatestArrivalListView.as_view()),

]

