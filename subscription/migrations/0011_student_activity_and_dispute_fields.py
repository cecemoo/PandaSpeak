from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("subscription", "0010_subscription_plus_promo_access_until"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name="subscription",
            name="dispute_charge_id",
            field=models.CharField(blank=True, default="", max_length=300),
        ),
        migrations.AddField(
            model_name="subscription",
            name="dispute_external_id",
            field=models.CharField(blank=True, default="", max_length=300),
        ),
        migrations.AddField(
            model_name="subscription",
            name="dispute_provider",
            field=models.CharField(blank=True, default="", max_length=20),
        ),
        migrations.AddField(
            model_name="subscription",
            name="dispute_status",
            field=models.CharField(blank=True, default="", max_length=40),
        ),
        migrations.AddField(
            model_name="subscription",
            name="disputed_at",
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="subscription",
            name="is_disputed",
            field=models.BooleanField(default=False),
        ),
        migrations.CreateModel(
            name="StudentActivity",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("activity_type", models.CharField(default="page_access", max_length=80)),
                ("method", models.CharField(blank=True, max_length=10)),
                ("path", models.CharField(max_length=500)),
                ("view_name", models.CharField(blank=True, max_length=200)),
                ("ip_address", models.GenericIPAddressField(blank=True, null=True)),
                ("user_agent", models.TextField(blank=True)),
                ("response_status", models.PositiveSmallIntegerField(blank=True, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True, db_index=True)),
                ("user", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="student_activities", to=settings.AUTH_USER_MODEL)),
            ],
            options={"ordering": ["-created_at"]},
        ),
        migrations.AddIndex(
            model_name="studentactivity",
            index=models.Index(fields=["user", "-created_at"], name="subscriptio_user_id_47b7c1_idx"),
        ),
        migrations.AddIndex(
            model_name="studentactivity",
            index=models.Index(fields=["activity_type", "-created_at"], name="subscriptio_activit_14b42c_idx"),
        ),
    ]
