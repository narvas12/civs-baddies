# Generated by Django 5.0.4 on 2024-04-28 09:29

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0004_order_order_number'),
    ]

    operations = [
        migrations.RenameField(
            model_name='order',
            old_name='user',
            new_name='buyer',
        ),
    ]
