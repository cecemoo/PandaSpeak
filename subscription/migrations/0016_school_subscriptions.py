from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import decimal

class Migration(migrations.Migration):
    dependencies = [("subscription", "0015_blocked_purchase_email"), migrations.swappable_dependency(settings.AUTH_USER_MODEL)]
    operations = [
        migrations.CreateModel(name="SchoolSubscriptionBatch", fields=[
            ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
            ("school_name", models.CharField(max_length=200)),
            ("payment_method", models.CharField(max_length=20, choices=[("card","Credit card"),("cash","Cash"),("wire","Wire transfer")])),
            ("amount_received", models.DecimalField(max_digits=10, decimal_places=2, default=decimal.Decimal("0.00"))),
            ("unit_price", models.DecimalField(max_digits=8, decimal_places=2, default=decimal.Decimal("15.00"))),
            ("payment_reference", models.CharField(max_length=200, blank=True)),
            ("payment_received_at", models.DateTimeField(null=True, blank=True)),
            ("created_at", models.DateTimeField(auto_now_add=True)),
            ("created_by", models.ForeignKey(to=settings.AUTH_USER_MODEL, on_delete=django.db.models.deletion.PROTECT)),
        ]),
        migrations.CreateModel(name="SchoolSubscriptionEnrollment", fields=[
            ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
            ("access_until", models.DateTimeField(null=True, blank=True)),
            ("created_at", models.DateTimeField(auto_now_add=True)),
            ("batch", models.ForeignKey(to="subscription.schoolsubscriptionbatch", related_name="enrollments", on_delete=django.db.models.deletion.PROTECT)),
            ("student", models.ForeignKey(to=settings.AUTH_USER_MODEL, on_delete=django.db.models.deletion.PROTECT)),
        ]),
        migrations.AddConstraint(model_name="schoolsubscriptionenrollment", constraint=models.UniqueConstraint(fields=["batch","student"], name="unique_school_batch_student")),
    ]
