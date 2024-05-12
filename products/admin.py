from django.contrib import admin
from .models import ProductCategory, Product, Variation




@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}
    list_display = ('id','name', 'category', 'quantity', 'created_at', 'updated_at')
    search_fields = ('name', 'category__category_name')

@admin.register(ProductCategory)
class ProductCategoryAdmin(admin.ModelAdmin):
    list_display = ['id','name']


@admin.register(Variation)
class VariationAdmin(admin.ModelAdmin):
   list_display = ['id','product_variant', 'color','size', "stock_quantity"]
    