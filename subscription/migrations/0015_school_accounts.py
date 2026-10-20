from decimal import Decimal
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("subscription", "0014_subscription_consentevent"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="SchoolAccount",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=200, unique=True)),
                ("contact_email", models.EmailField(blank=True, max_length=254)),
                ("annual_price", models.DecimalField(decimal_places=2, default=Decimal("15.00"), max_digits=8)),
                ("is_active", models.BooleanField(default=True)),
            ],
        ),
        migrations.CreateModel(
            name="SchoolEnrollment",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("starts_at", models.DateTimeField()),
                ("expires_at", models.DateTimeField()),
                ("agreed_price", models.DecimalField(decimal_places=2, max_digits=8)),
                ("payment_reference", models.CharField(blank=True, max_length=200)),
                ("revoked_at", models.DateTimeField(blank=True, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("school", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="enrollments", to="subscription.schoolaccount")),
                ("student", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="school_enrollments", to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
