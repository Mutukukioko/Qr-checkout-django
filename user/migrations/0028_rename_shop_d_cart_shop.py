# Generated by Django 4.1.4 on 2023-04-12 12:53

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0027_rename_shop_cart_shop_d'),
    ]

    operations = [
        migrations.RenameField(
            model_name='cart',
            old_name='shop_d',
            new_name='shop',
        ),
    ]
