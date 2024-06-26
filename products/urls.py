from django.urls import path


from .views import (
                    
                   
                    CoverPageCarouselAPIView,
                    CoverPageCarouselListView,
                    LatestArivalAPIView,
                    CategoryCreateAPIView,
                    LatestArrivalListView,
                    ProductCategoryListAPIView,
                    ProductCreateAPIView,
                    ProductDeleteAPIView,
                    ProductDetailView, 
                    ProductListAPIView,
                    SuperCategoryCreateAPIView,
                    # ProductListCreateAPIView,
                    ProductRetrieveUpdateDestroyAPIView,
                    ProductUpdateAPIView,
                    VariationListCreateAPIView,
                    VariationRetrieveUpdateDestroyAPIView,
                    VariationListAPIView,
                    )



urlpatterns = [
    path('products/create/', ProductCreateAPIView.as_view()),
    path('product/<int:pk>/', ProductUpdateAPIView.as_view()),

    # path('add_products/', ProductListCreateAPIView.as_view()),
    path('product/update/<int:pk>/', ProductRetrieveUpdateDestroyAPIView.as_view()),
    path('product/detail/<int:pk>/', ProductDetailView.as_view()),

    path('products/list/', ProductListAPIView.as_view()),
    path('products/delete/', ProductDeleteAPIView.as_view()),

    path('super-categories/add/', SuperCategoryCreateAPIView.as_view()),

    path('categories/add/', CategoryCreateAPIView.as_view()),
    path('categories/list/', ProductCategoryListAPIView.as_view()),

    path('variations/', VariationListAPIView.as_view()),
    path('variations/<int:pk>/', VariationRetrieveUpdateDestroyAPIView.as_view()),
    path('variations/product/<int:product_id>/', VariationListCreateAPIView.as_view()),


    path('coverpage-carousel/add/', CoverPageCarouselAPIView.as_view()),
    path('cover-page-carousels/', CoverPageCarouselListView.as_view()),

    path('latest-arrivals/add/', LatestArivalAPIView.as_view()),
    path('latest-arrivals/', LatestArrivalListView.as_view()),

]

