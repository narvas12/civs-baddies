# Generated by Django 5.0.4 on 2024-10-09 14:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cart', '0005_alter_wishlist_added_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='wishlist',
            name='slug',
            field=models.SlugField(blank=True, max_length=100, null=True, unique=True),
        ),
    ]
