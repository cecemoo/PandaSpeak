from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("subscription", "0017_align_index_names"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]
    operations = [
        migrations.CreateModel(
            name="SchoolPayment",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("method", models.CharField(max_length=8, choices=[("card", "Credit card"), ("cash", "Cash"), ("wire", "Wire transfer")])),
                ("amount", models.DecimalField(max_digits=10, decimal_places=2)),
                ("reference", models.CharField(max_length=200, blank=True)),
                ("stripe_session_id", models.CharField(max_length=255, blank=True, unique=True, null=True)),
                ("received_at", models.DateTimeField(null=True, blank=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("school", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="payments", to="subscription.schoolaccount")),
                ("confirmed_by", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name="schoolenrollment",
            name="payment",
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name="enrollments", to="subscription.schoolpayment"),
        ),
    ]
