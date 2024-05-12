# Generated by Django 5.0.3 on 2024-04-13 19:58

import django.db.models.deletion
import products.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0002_variation_color_variation_size'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='category',
            field=models.ForeignKey(default=products.models.get_default_product_category, on_delete=models.SET(products.models.get_default_product_category), related_name='product_list', to='products.productcategory'),
        ),
        migrations.AlterUniqueTogether(
            name='variation',
            unique_together={('size', 'color')},
        ),
        migrations.CreateModel(
            name='ProductVariation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='products.product')),
                ('variation', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='products.variation')),
            ],
        ),
    ]
