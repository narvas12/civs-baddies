from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model
from cloudinary.models import CloudinaryField


User = get_user_model()


class Supercategory(models.Model):
    name = models.CharField(max_length=15)

    def __str__(self) -> str:
        return self.name

def get_default_product_super_category():
    return Supercategory.objects.get_or_create(name="Super_Others")[0]

class ProductCategory(models.Model):
    super_category = models.ForeignKey(Supercategory, related_name='super_category', on_delete=models.SET(get_default_product_super_category), null=True)
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


class ProductImage(models.Model):
    product = models.ForeignKey('Product', on_delete=models.CASCADE)
    image = CloudinaryField("product/image/")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Image for {self.product.name}"


class Size(models.Model):
    name = models.CharField(max_length=100)
    quantity = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.name


class Color(models.Model):
    name = models.CharField(max_length=100)
    quantity = models.PositiveIntegerField(default=0)
    sizes = models.ManyToManyField(Size, blank=True)

    def __str__(self):
        return self.name


class Variation(models.Model):
    product_variant = models.ForeignKey(Product, related_name='variations', on_delete=models.CASCADE, null=True, blank=True)
    image = models.ForeignKey(ProductImage, related_name='variations', on_delete=models.CASCADE)
    colors = models.ManyToManyField(Color, related_name='variations', blank=True)  
    price = models.DecimalField(max_digits=20, decimal_places=2, default=0)

    def __str__(self):
        colors_str = ', '.join(str(color) for color in self.colors.all())
        return f"{self.product_variant} - {colors_str}"

    

class LatestArival(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    image = CloudinaryField("product/image/latest", blank=True)


class CoverPageCarousel(models.Model):
    images = CloudinaryField("product/image/coverpage", blank=True)