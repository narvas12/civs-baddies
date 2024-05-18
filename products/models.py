from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model
from cloudinary.models import CloudinaryField


User = get_user_model()

class ProductCategory(models.Model):
    name = models.CharField(unique=True, max_length=100)
    icon = CloudinaryField("product/category/icons/", blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("Product Category")
        verbose_name_plural = _("Product Categories")

    def __str__(self):
        return self.name

    
def get_default_product_category():
    return ProductCategory.objects.get_or_create(name="Others")[0]


class Product(models.Model):
    product_tag = models.CharField(max_length=10, default="TS-001")
    category = models.ForeignKey(ProductCategory, related_name="product_list", on_delete=models.SET(get_default_product_category))
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)  
    desc = models.TextField(_("Description"), blank=True)
    image = CloudinaryField("product/images/", blank=True)
    price = models.DecimalField(decimal_places=2, max_digits=10)
    discounted_percentage = models.DecimalField(decimal_places=2, max_digits=10, blank=True, null=True) 
    quantity = models.PositiveIntegerField(default=1)
    initial_stock_quantity = models.PositiveIntegerField(default=0) 
    is_suspended = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    
    class Meta:
        ordering = ("-created_at",)

    def __str__(self):
        return self.name if self.name else "Product (No Name)"


class Variation(models.Model):
    product_variant = models.ForeignKey(Product, on_delete=models.CASCADE)
    size = models.CharField(max_length=100, null=True, blank=True)
    color = models.CharField(max_length=100, null=True, blank=True)
    price = models.DecimalField(max_digits=20, decimal_places=2, default=0)
    image = CloudinaryField("product/images/variations", blank=True)
    stock_quantity = models.PositiveIntegerField(default=0)


    def __str__(self):
        return f"{self.product_variant}"