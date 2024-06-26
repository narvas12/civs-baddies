# Generated by Django 5.0.3 on 2024-04-14 10:15

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cart', '0003_remove_cartitem_variation_cartitem_color_and_more'),
        ('products', '0006_remove_variation_product_product_variation'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='product',
            name='variation',
        ),
        migrations.AddField(
            model_name='color',
            name='quantity',
            field=models.CharField(default=1, max_length=100),
        ),
        migrations.AddField(
            model_name='product',
            name='Size',
            field=models.ForeignKey(default=0, on_delete=django.db.models.deletion.DO_NOTHING, to='products.size'),
        ),
        migrations.AddField(
            model_name='product',
            name='color',
            field=models.ForeignKey(default=0, on_delete=django.db.models.deletion.DO_NOTHING, to='products.color'),
        ),
        migrations.AddField(
            model_name='size',
            name='quantity',
            field=models.CharField(default=1, max_length=100),
        ),
        migrations.DeleteModel(
            name='Variation',
        ),
    ]
