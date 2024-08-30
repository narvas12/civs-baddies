import random
import string
from django.contrib.auth import get_user_model
from django.db import models
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _
from orders.managers import OrderManager
from products.models import Product, Variation
from users.models import Address, CustomUser
from users.models import Address, CustomUser


class Order(models.Model):
    PENDING = "P"
    COMPLETED = "C"
    SHIPPED = "S"
    CANCELED = "X"

    STATUS_CHOICES = (
        (PENDING, _("pending")),
        (COMPLETED, _("completed")),
        (SHIPPED, _("shipped")),
        (CANCELED, _("canceled")),
    )

    buyer = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='orders')
    order_number = models.CharField(max_length=250, blank=True, null=True)
    status = models.CharField(max_length=1, choices=STATUS_CHOICES, default=PENDING)
    is_paid = models.BooleanField(default=False)
    shipping_address = models.ForeignKey(Address, related_name="shipping_orders", on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    objects = OrderManager()

    class Meta:
        ordering = ("-created_at",)

    @cached_property
    def total_cost(self):
        items = self.orderitems.all()

    def get_full_name(self):
        return f"{self.buyer.first_name} {self.buyer.last_name}"

    def save(self, *args, **kwargs):

        random_part = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
        random_part_formatted = f"{random_part[:4]}-{random_part[4:]}"


        self.order_number = f"{self.buyer.customer_id}-{random_part_formatted}"
        
        super(Order, self).save(*args, **kwargs)
    
    @staticmethod
    def create_order(buyer, address, is_paid=False):

        order = Order()
        order.buyer = buyer
        order.shipping_address = address
        order.is_paid = is_paid
        order.save()
        return order


class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name="orderitems", on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    variation = models.ForeignKey(Variation, on_delete=models.SET_NULL, null=True, blank=True)  # Link to variation
    quantity = models.PositiveIntegerField()
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    @cached_property
    def get_cost(self):
        return self.quantity * self.product.price

    @staticmethod
    def create_order_item(order, product, quantity, variation=None):
        total = quantity * product.price  
        order_item = OrderItem(
            order=order,
            product=product,
            quantity=quantity,
            total=total,
            variation=variation  # Save the variation to the order item
        )
        return order_item
    


class Transaction(models.Model):
    order = models.ForeignKey(Order, related_name='transactions', on_delete=models.CASCADE) 
    reference = models.CharField(max_length=255, unique=True)  
    amount = models.DecimalField(max_digits=10, decimal_places=2) 
    status = models.CharField(max_length=255)  
    gateway = models.CharField(max_length=255, blank=True) 
    charged_at = models.DateTimeField(blank=True, null=True)  
    message = models.TextField(blank=True) 

    def __str__(self):
        return f"Transaction for Order {self.order.order_number} (Ref: {self.reference})"