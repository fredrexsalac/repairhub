from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('appointments', '0008_contactmessagereply'),
    ]

    operations = [
        migrations.AddField(
            model_name='appointment',
            name='parts_ordered',
            field=models.BooleanField(default=False),
        ),
    ]
