import django_filters
from .models import Product, ProductCategory

class ProductFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr='icontains')  # Case-insensitive search

    class Meta:
        model = Product
        fields = ['category', 'name', 'price']  # Add more fields as needed for searching


class ProductCategoryFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(field_name='category_name', lookup_expr='icontains')

    class Meta:
        model = ProductCategory
        fields = ['name']