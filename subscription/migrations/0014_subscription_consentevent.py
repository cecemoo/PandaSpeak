from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [("subscription", "0013_subscription_checkout_terms_acceptance")]

    operations = [
        migrations.CreateModel(
            name="SubscriptionConsentEvent",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("accepted_at", models.DateTimeField(auto_now_add=True, db_index=True)),
                ("terms_version", models.CharField(max_length=40)),
                ("terms_accepted", models.BooleanField(default=True)),
                ("faq_accepted", models.BooleanField(default=True)),
                ("payment_provider", models.CharField(max_length=20, blank=True)),
                ("checkout_status", models.CharField(max_length=30, default="initiated")),
                ("provider_session_id", models.CharField(max_length=300, blank=True)),
                ("ip_address", models.GenericIPAddressField(blank=True, null=True)),
                ("user_agent", models.TextField(blank=True)),
                ("user", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="subscription_consent_events", to="account.customuser")),
            ],
            options={"ordering": ["-accepted_at"]},
        ),
    ]
