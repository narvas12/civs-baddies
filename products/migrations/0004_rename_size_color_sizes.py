# Generated by Django 5.0.4 on 2024-08-30 05:01

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0003_rename_color_variation_colors'),
    ]

    operations = [
        migrations.RenameField(
            model_name='color',
            old_name='size',
            new_name='sizes',
        ),
    ]
