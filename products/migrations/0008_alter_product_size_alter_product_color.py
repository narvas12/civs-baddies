# Generated by Django 5.0.3 on 2024-04-14 10:20

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0007_remove_product_variation_color_quantity_product_size_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='Size',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.DO_NOTHING, to='products.size'),
        ),
        migrations.AlterField(
            model_name='product',
            name='color',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.DO_NOTHING, to='products.color'),
        ),
    ]
