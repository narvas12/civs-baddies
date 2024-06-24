from decimal import Decimal
from django.apps import apps
from django.db.models import Count
from django.db import models
from datetime import datetime, timedelta
from django.db.models import Prefetch


class OrderManager(models.Manager):
    def get_trending_products(self):
        now = datetime.now()

        one_month_ago = now - timedelta(days=30)

        OrderItem = apps.get_model('orders', 'OrderItem')

        trending_products = OrderItem.objects.filter(order__created_at__gte=one_month_ago).values('product__name').annotate(total=Count('product')).order_by('-total')[:5]

        return trending_products
    

    def get_user_orders_with_items(self, user):
        orders = self.prefetch_related('orderitems__product').filter(buyer=user)
        order_list = []

        for order in orders:
            order_data = {
                'id': order.id,
                'buyer': order.buyer.id,
                'order_number': order.order_number,
                'status': order.status,
                'is_paid': order.is_paid,
                'shipping_address': order.shipping_address.id if order.shipping_address else None,
                'created_at': order.created_at,
                'orderitems': [],
                'total_amount': Decimal('0.00'),
                'discount': Decimal('0.00'),
                'tax': Decimal('0.00')
            }

            total_amount = Decimal('0.00')
            discount_amount = Decimal('0.00')

            for item in order.orderitems.all():
                product = item.product
                item_data = {
                    'product': product.id,
                    'name': product.name,
                    'image': product.image.url if product.image else None,
                    'price': product.price,
                    'quantity': item.quantity,
                    'total': item.total
                }
                order_data['orderitems'].append(item_data)

                total_amount += item.total
                if product.discounted_percentage:
                    discount_amount += Decimal(item.quantity) * product.price * product.discounted_percentage / Decimal('100')

            order_data['total_amount'] = total_amount
            order_data['discount'] = discount_amount
            order_data['tax'] = total_amount * Decimal('0.10')  # Assuming a flat tax rate of 10%

            order_list.append(order_data)

        return order_list