from decimal import Decimal
from django.apps import apps
from django.db.models import Count
from django.db import models
from datetime import datetime, timedelta
from django.db.models import Prefetch
from django.core.exceptions import ObjectDoesNotExist


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

    def list_orders(self):
        orders = self.prefetch_related('orderitems__product').all()
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
    

    def get_order_details(self, order_id):
        Order = apps.get_model('your_app_name', 'Order')
        order = Order.objects.prefetch_related('orderitems__product').filter(id=order_id).first()
        
        if not order:
            raise Order.DoesNotExist("Order not found")
        
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

        return order_data

    
    def get_order_details(self, user, order_id):
        try:
            order = self.prefetch_related('orderitems__product').get(id=order_id, buyer=user)
            order_items = order.orderitems.all()

            order_data = {
                'id': order.id,
                'buyer': order.buyer.id,
                'order_number': order.order_number,
                'status': order.status,
                'is_paid': order.is_paid,
                'shipping_address': {
                    'id': order.shipping_address.id,
                    'apartment_address': order.shipping_address.apartment_address,
                    'street': order.shipping_address.street_address,
                    'city': order.shipping_address.city,
                    'country': order.shipping_address.country.name,
                },
                'created_at': order.created_at,
                'orderitems': []
            }

            total_amount = Decimal(0)
            discount = Decimal(0)
            tax_rate = Decimal(0.10)  

            for item in order_items:
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
                    discount += (product.discounted_percentage / 100) * item.quantity * product.price

            tax = total_amount * tax_rate

            order_data['total_amount'] = total_amount
            order_data['discount'] = discount
            order_data['tax'] = tax

            return order_data
        except ObjectDoesNotExist:
            raise ObjectDoesNotExist("Order not found")
        except Exception as e:
            raise Exception(f"An unexpected error occurred: {str(e)}")