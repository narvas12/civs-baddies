from django.db import models
from products.models import Product, Variation
from users.models import CustomUser
from rest_framework.validators import ValidationError



class CartItem(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='cart_items', null=True, blank=True, default="")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    variation = models.ForeignKey(Variation, on_delete=models.DO_NOTHING, default="", null=True, blank=True)

    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    discounted_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    abandoned = models.BooleanField(default=False)
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):

        self.total_price = self.quantity * self.product.price

        if self.product.discounted_percentage:
            discount_percentage = self.product.discounted_percentage / 100
            self.discounted_price = self.total_price * (1 - discount_percentage)
            self.discount = self.total_price - self.discounted_price 
        else:
            self.discounted_price = self.total_price
            self.discount = 0.00 

        super().save(*args, **kwargs)  

    def clean_quantity(self):
        if self.quantity <= 0:
            raise ValidationError('Quantity must be a positive integer.')
        return self.quantity
        


class WishlistItem(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)  
    product = models.ForeignKey(Product, on_delete=models.CASCADE)  
    added_date = models.DateTimeField(auto_now_add=True)  

    class Meta:
        unique_together = ('user', 'product')

    def __str__(self):
        return f"{self.user.username}'s wishlist: {self.product.name}"