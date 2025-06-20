# Generated by Django 5.2.1 on 2025-05-22 19:33

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('host', '0009_alter_hotel_options'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='amenity',
            options={'verbose_name': 'Удобства', 'verbose_name_plural': 'Удобства'},
        ),
        migrations.AlterModelOptions(
            name='booking',
            options={'verbose_name': 'Бронирования', 'verbose_name_plural': 'Бронирования'},
        ),
        migrations.AlterModelOptions(
            name='hotelservice',
            options={'verbose_name': 'Услуги отеля', 'verbose_name_plural': 'Услуги отеля'},
        ),
        migrations.AlterModelOptions(
            name='payment',
            options={'verbose_name': 'Платеж', 'verbose_name_plural': 'Платеж'},
        ),
        migrations.AlterModelOptions(
            name='promotion',
            options={'verbose_name': 'Акции', 'verbose_name_plural': 'Акции'},
        ),
        migrations.AlterModelOptions(
            name='review',
            options={'verbose_name': 'Отзывы', 'verbose_name_plural': 'Отзывы'},
        ),
        migrations.AlterModelOptions(
            name='room',
            options={'verbose_name': 'Номера', 'verbose_name_plural': 'Номера'},
        ),
    ]
