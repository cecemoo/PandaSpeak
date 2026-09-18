from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('course', '0014_groupclassrequest'),
    ]

    operations = [
        migrations.AddField(
            model_name='groupclassrequest',
            name='requested_price',
            field=models.PositiveIntegerField(blank=True, null=True, help_text='Price per student proposed by the student.'),
        ),
    ]
