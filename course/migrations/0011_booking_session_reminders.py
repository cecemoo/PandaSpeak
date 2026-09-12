from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('course', '0010_booking_payout_transferred_at'),
    ]

    operations = [
        migrations.AddField(
            model_name='booking',
            name='reminder_24h_sent_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='booking',
            name='reminder_1h_sent_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
