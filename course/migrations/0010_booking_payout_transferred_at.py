from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('course', '0009_booking_session_review'),
    ]

    operations = [
        migrations.AddField(
            model_name='booking',
            name='payout_transferred_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
