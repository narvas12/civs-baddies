# Generated by Django 5.0.4 on 2024-10-09 09:02

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cart', '0002_wishlist_delete_wishlistitem'),
        ('products', '0006_variation_image'),
    ]

    operations = [
        migrations.AlterField(
            model_name='wishlist',
            name='added_date',
            field=models.DateTimeField(verbose_name=datetime.datetime(2024, 10, 9, 9, 2, 47, 442054, tzinfo=datetime.timezone.utc)),
        ),
        migrations.AlterField(
            model_name='wishlist',
            name='product',
            field=models.ManyToManyField(blank=True, related_name='wish_list', to='products.product'),
        ),
    ]
