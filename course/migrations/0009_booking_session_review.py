from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('course', '0008_booking_is_test_booking'),
    ]

    operations = [
        migrations.AddField(
            model_name='booking',
            name='review_rating',
            field=models.PositiveSmallIntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='booking',
            name='review_comment',
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name='booking',
            name='reviewed_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
