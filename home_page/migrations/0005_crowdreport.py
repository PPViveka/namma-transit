from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('home_page', '0004_add_mode_and_interchange'),
    ]

    operations = [
        migrations.CreateModel(
            name='CrowdReport',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(
                    choices=[
                        ('EMPTY', 'Empty'),
                        ('MODERATE', 'Moderate'),
                        ('FULL', 'Full'),
                        ('OVERCROWDED', 'Overcrowded'),
                    ],
                    max_length=15,
                )),
                ('reported_at', models.DateTimeField(auto_now_add=True)),
                ('bus', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='crowd_reports',
                    to='home_page.BusInformation',
                )),
            ],
            options={'get_latest_by': 'reported_at'},
        ),
    ]
