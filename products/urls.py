from django.urls import path


from .views import (
                    
                   
                    CoverPageCarouselAPIView,
                    LatestArivalAPIView,
                    CategoryCreateAPIView,
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
    path('create_products/', ProductCreateAPIView.as_view()),
    path('product/<int:pk>/', ProductUpdateAPIView.as_view()),

    # path('add_products/', ProductListCreateAPIView.as_view()),
    path('update_product/<int:pk>/', ProductRetrieveUpdateDestroyAPIView.as_view()),
    path('product-detail/<int:pk>/', ProductDetailView.as_view()),

    path('products_list/', ProductListAPIView.as_view()),
    path('delete_products/', ProductDeleteAPIView.as_view()),

    path('super-categories/add/', SuperCategoryCreateAPIView.as_view()),

    path('categories/add/', CategoryCreateAPIView.as_view()),
    path('categories/list/', ProductCategoryListAPIView.as_view()),

    path('variations/', VariationListCreateAPIView.as_view()),
    path('list-variations/', VariationListAPIView.as_view()),
    path('variations/<int:pk>/', VariationRetrieveUpdateDestroyAPIView.as_view()),


    path('coverpage-carousel/add/', CoverPageCarouselAPIView.as_view()),
    path('latest-arrivals/add/', LatestArivalAPIView.as_view()),

]

