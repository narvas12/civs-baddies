from django.contrib import admin
from .models import CoverPageCarousel, LatestArival, ProductCategory, Product, Supercategory, Variation




@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}
    list_display = ('id','name', 'category', 'quantity', 'created_at', 'updated_at')
    search_fields = ('name', 'category__category_name')



@admin.register(Supercategory)
class ProductCategoryAdmin(admin.ModelAdmin):
    list_display = ['name']


@admin.register(ProductCategory)
class ProductCategoryAdmin(admin.ModelAdmin):
    list_display = ['name']


@admin.register(Variation)
class VariationAdmin(admin.ModelAdmin):
   list_display = ['id','product_variant', 'color','size', "stock_quantity"]
    

@admin.register(LatestArival)
class LatestArivalAdmin(admin.ModelAdmin):
    class Meta:
        list_diaplay = ['id','product']

@admin.register(CoverPageCarousel)
class LatestArivalAdmin(admin.ModelAdmin):
    class Meta:
        list_diaplay = ['id']