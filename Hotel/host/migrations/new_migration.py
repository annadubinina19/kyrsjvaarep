from django.db import migrations

class Migration(migrations.Migration):
    dependencies = [
        ('host', '0015_alter_hotel_location'),
    ]

    operations = [
        migrations.RunSQL(
            sql='CREATE INDEX IF NOT EXISTS idx_hotel_location_nocase ON host_hotel(location COLLATE NOCASE);',
            reverse_sql='DROP INDEX IF EXISTS idx_hotel_location_nocase;'
        ),
    ] 