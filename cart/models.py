import uuid
from django.db import models
from products.models import Product, Variation
from users.models import CustomUser
from django.utils.text import slugify
from django.utils import timezone


class CartItem(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='cart_items', null=True, blank=True, default="")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    variation = models.ForeignKey(Variation, on_delete=models.DO_NOTHING, null=True, blank=True)  
    color = models.CharField(max_length=50, null=True, blank=True)  
    size = models.CharField(max_length=50, null=True, blank=True) 
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    discounted_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    abandoned = models.BooleanField(default=False)
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        # Ensure product has a price
        if not self.product.price or self.product.price <= 0:
            raise ValueError("Product price must be set and greater than 0 before saving the cart item.")


        self.total_price = self.quantity * self.product.price


        if self.product.discounted_percentage:
            discount_percentage = self.product.discounted_percentage / 100
            self.discounted_price = self.total_price * (1 - discount_percentage)
            self.discount = self.total_price - self.discounted_price
        else:
            self.discounted_price = self.total_price
            self.discount = 0.00

        super().save(*args, **kwargs)



class WishList(models.Model):
    product = models.ManyToManyField(Product, related_name="wish_list", blank=True)
    session_key = models.CharField(max_length=32, null=True, blank=True)
    slug = models.SlugField(unique=True, blank=True, null=True)
    added_date = models.DateTimeField(timezone.now())


    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(f"{self.product.name}-{self.added_date}")
        super().save(*args, **kwargs)