# Generated by Django 5.0.4 on 2024-05-06 13:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0013_rename_discounted_price_product_discounted_percentage'),
    ]

    operations = [
        migrations.AlterField(
            model_name='variation',
            name='color',
            field=models.CharField(max_length=100),
        ),
        migrations.AlterField(
            model_name='variation',
            name='size',
            field=models.CharField(max_length=100),
        ),
    ]
