from django.urls import path


from .views import (
                    
                   
                    ProductCategoryCreateAPIView,
                    ProductCategoryListAPIView,
                    ProductCreateAPIView,
                    ProductDeleteAPIView, 
                    ProductListAPIView,
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

    path('products_list/', ProductListAPIView.as_view()),
    path('delete_products/', ProductDeleteAPIView.as_view()),
    path('categories/add/', ProductCategoryCreateAPIView.as_view()),
    path('categories/list/', ProductCategoryListAPIView.as_view()),

    path('variations/', VariationListCreateAPIView.as_view()),
    path('list-variations/', VariationListAPIView.as_view()),
    path('variations/<int:pk>/', VariationRetrieveUpdateDestroyAPIView.as_view()),
]

