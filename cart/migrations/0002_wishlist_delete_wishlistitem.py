# Generated by Django 5.0.4 on 2024-10-09 09:02

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cart', '0001_initial'),
        ('products', '0006_variation_image'),
    ]

    operations = [
        migrations.CreateModel(
            name='WishList',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('session_key', models.CharField(blank=True, max_length=32, null=True)),
                ('slug', models.SlugField(blank=True, null=True, unique=True)),
                ('added_date', models.DateTimeField(verbose_name=datetime.datetime(2024, 10, 9, 9, 2, 13, 84751, tzinfo=datetime.timezone.utc))),
                ('product', models.ManyToManyField(blank=True, null=True, related_name='wish_list', to='products.product')),
            ],
        ),
        migrations.DeleteModel(
            name='WishlistItem',
        ),
    ]
