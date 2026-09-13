from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("subscription", "0006_subscription_access_until_subscription_is_cancelled"),
    ]

    operations = [
        migrations.AddField(
            model_name="subscription",
            name="stripe_subscription_id",
            field=models.CharField(blank=True, max_length=300, null=True),
        ),
    ]
