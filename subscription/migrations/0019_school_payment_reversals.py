from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("subscription", "0018_school_payments")]
    operations = [
        migrations.AddField(
            model_name="schoolpayment",
            name="reversed_at",
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
