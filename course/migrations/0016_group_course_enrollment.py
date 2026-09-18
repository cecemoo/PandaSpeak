from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [('course', '0015_groupclassrequest_requested_price')]

    operations = [
        migrations.AddField(
            model_name='course',
            name='minimum_students',
            field=models.PositiveIntegerField(default=1, help_text='Minimum paid students required for a group class to proceed.'),
        ),
        migrations.AddField(
            model_name='course',
            name='enrollment_status',
            field=models.CharField(choices=[('open','Open for Enrollment'),('confirmed','Confirmed'),('proceed','Proceed Below Minimum'),('canceled','Canceled')], default='open', max_length=12),
        ),
    ]
