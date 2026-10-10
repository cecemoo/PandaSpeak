from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("account", "0012_leadmagnetsignup")]

    operations = [
        migrations.AddField(model_name="customuser", name="stripe_connect_terms_accepted_at", field=models.DateTimeField(blank=True, null=True)),
        migrations.AddField(model_name="customuser", name="stripe_connect_terms_version", field=models.CharField(max_length=40, blank=True, default="")),
    ]
