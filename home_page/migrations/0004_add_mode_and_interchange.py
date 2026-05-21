from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home_page', '0003_businformation_bus_viaroad'),
    ]

    operations = [
        migrations.AddField(
            model_name='businformation',
            name='mode',
            field=models.CharField(
                choices=[
                    ('BUS', 'BMTC Bus'),
                    ('METRO', 'Namma Metro'),
                    ('RAIL', 'Suburban Rail'),
                    ('AUTO', 'Auto Rickshaw'),
                ],
                default='BUS',
                max_length=10,
            ),
        ),
        migrations.CreateModel(
            name='Interchange',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('stop_name', models.CharField(max_length=255, unique=True)),
                ('modes_available', models.CharField(max_length=100)),
                ('metro_station_name', models.CharField(blank=True, max_length=255)),
                ('rail_station_name', models.CharField(blank=True, max_length=255)),
            ],
        ),
    ]
