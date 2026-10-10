from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("subscription", "0011_student_activity_and_dispute_fields")]

    operations = [
        migrations.AddField(
            model_name="subscription",
            name="pending_stripe_checkout_id",
            field=models.CharField(max_length=300, blank=True, default=""),
        ),
    ]
