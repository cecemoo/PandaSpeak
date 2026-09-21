from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("subscription", "0008_subscription_plus_fields"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Referral",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("code", models.CharField(db_index=True, max_length=32)),
                ("rewarded_at", models.DateTimeField(blank=True, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("referred_user", models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name="referral_received", to=settings.AUTH_USER_MODEL)),
                ("referrer", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="referrals_made", to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name="PlusReward",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("status", models.CharField(choices=[("available", "Available"), ("applied", "Applied"), ("void", "Void")], default="available", max_length=12)),
                ("applied_at", models.DateTimeField(blank=True, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("referral", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="plus_rewards", to="subscription.referral")),
                ("user", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="plus_rewards", to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddConstraint(
            model_name="plusreward",
            constraint=models.UniqueConstraint(fields=("user", "referral"), name="unique_plus_reward_per_referral_user"),
        ),
    ]
