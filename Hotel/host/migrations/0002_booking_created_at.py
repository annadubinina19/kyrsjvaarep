# Generated by Django 5.2.1 on 2025-05-21 18:37

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('host', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='booking',
            name='created_at',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]
