from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('course', '0012_reschedulerequest'),
    ]

    operations = [
        migrations.AddField(
            model_name='course',
            name='session_type',
            field=models.CharField(
                choices=[
                    ('private', 'Private Tutoring'),
                    ('group', 'Group Tutoring'),
                ],
                default='private',
                max_length=10,
            ),
        ),
        migrations.AddField(
            model_name='course',
            name='max_students',
            field=models.PositiveIntegerField(
                default=1,
                help_text='Maximum number of students who can book the same session.',
            ),
        ),
    ]
