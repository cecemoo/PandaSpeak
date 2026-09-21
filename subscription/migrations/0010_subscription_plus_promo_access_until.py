from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("subscription", "0009_referral_plusreward")]

    operations = [
        migrations.AddField(
            model_name="subscription",
            name="plus_promo_access_until",
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
