from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("subscription", "0012_subscription_pending_stripe_checkout")]

    operations = [
        migrations.AddField(
            model_name="subscription",
            name="checkout_terms_accepted_at",
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="subscription",
            name="checkout_terms_version",
            field=models.CharField(max_length=40, blank=True, default=""),
        ),
    ]
