# Generated by Django 4.1.4 on 2023-03-23 13:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0004_item'),
    ]

    operations = [
        migrations.AddField(
            model_name='item',
            name='brand',
            field=models.CharField(default='', max_length=254),
        ),
        migrations.AddField(
            model_name='item',
            name='category',
            field=models.CharField(choices=[('Kitchen', 'Home appliance'), ('Cloths', 'Shoes'), ('electricals', 'non electric')], max_length=254, null=True),
        ),
        migrations.AddField(
            model_name='item',
            name='quantity',
            field=models.CharField(default='', max_length=254),
        ),
        migrations.AddField(
            model_name='item',
            name='shop_id',
            field=models.CharField(default='', max_length=254),
        ),
    ]
