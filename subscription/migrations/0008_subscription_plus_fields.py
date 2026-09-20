from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('subscription', '0007_subscription_stripe_subscription_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='subscription',
            name='plus_stripe_subscription_id',
            field=models.CharField(blank=True, max_length=300, null=True),
        ),
        migrations.AddField(
            model_name='subscription',
            name='plus_is_active',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='subscription',
            name='plus_is_cancelled',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='subscription',
            name='plus_access_until',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
