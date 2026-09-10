from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('course', '0007_booking_dispute_details'),
    ]

    operations = [
        migrations.AddField(
            model_name='booking',
            name='is_test_booking',
            field=models.BooleanField(default=False),
        ),
    ]
