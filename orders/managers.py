from django.apps import apps
from django.db.models import Count
from django.db import models
from datetime import datetime, timedelta

class OrderManager(models.Manager):
    def get_trending_products(self):
        # Get the current date
        now = datetime.now()

        # Calculate the date one month ago
        one_month_ago = now - timedelta(days=30)

        OrderItem = apps.get_model('orders', 'OrderItem')

        # Get the top 5 most sold products in the last month
        trending_products = OrderItem.objects.filter(order__created_at__gte=one_month_ago).values('product__name').annotate(total=Count('product')).order_by('-total')[:5]

        return trending_products