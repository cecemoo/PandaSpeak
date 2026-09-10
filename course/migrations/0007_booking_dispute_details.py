from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('course', '0006_booking_session_tracking'),
    ]

    operations = [
        migrations.AddField(
            model_name='booking',
            name='issue_details',
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name='booking',
            name='issue_reported_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='booking',
            name='issue_resolved_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='booking',
            name='issue_resolution_note',
            field=models.TextField(blank=True),
        ),
    ]
