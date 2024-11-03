import django_filters
from django.db.models import Q
from .models import Product, ProductCategory, Color, Size

class ProductFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr='icontains')
    price_min = django_filters.NumberFilter(field_name="price", lookup_expr='gte')
    price_max = django_filters.NumberFilter(field_name="price", lookup_expr='lte')
    color = django_filters.CharFilter(method='filter_by_color')
    size = django_filters.CharFilter(method='filter_by_size')
    
    class Meta:
        model = Product
        fields = ['name', 'price', 'desc']

    def filter_by_color(self, queryset, name, value):
        return queryset.filter(variations__colors__name__icontains=value)

    def filter_by_size(self, queryset, name, value):
        return queryset.filter(variations__colors__sizes__name__icontains=value)


class ProductCategoryFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr='icontains')
    
    class Meta:
        model = ProductCategory
        fields = ['name', 'super_category']