# Generated by Django 5.0.4 on 2024-09-10 12:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0002_orderitem_color_orderitem_size'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='orderitem',
            name='variation',
        ),
        migrations.AlterField(
            model_name='orderitem',
            name='color',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='orderitem',
            name='size',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]
