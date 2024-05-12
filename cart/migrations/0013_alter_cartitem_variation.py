# Generated by Django 5.0.4 on 2024-05-07 10:30

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cart', '0012_alter_cartitem_variation'),
        ('products', '0016_variation_image_variation_price_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cartitem',
            name='variation',
            field=models.ForeignKey(blank=True, default='', null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='products.variation'),
        ),
    ]
