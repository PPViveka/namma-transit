from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home_page', '0005_crowdreport'),
    ]

    operations = [
        migrations.AddField(
            model_name='interchange',
            name='lat',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='interchange',
            name='lng',
            field=models.FloatField(blank=True, null=True),
        ),
    ]
