from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('course', '0011_booking_session_reminders'),
    ]

    operations = [
        migrations.CreateModel(
            name='RescheduleRequest',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('requested_at', models.DateTimeField(auto_now_add=True)),
                ('status', models.CharField(choices=[('pending', 'Pending'), ('accepted', 'Accepted'), ('declined', 'Declined')], default='pending', max_length=10)),
                ('responded_at', models.DateTimeField(blank=True, null=True)),
                ('booking', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='reschedule_request', to='course.booking')),
                ('original_timeslot', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='reschedule_requests_from', to='course.timeslot')),
                ('proposed_timeslot', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='reschedule_requests_to', to='course.timeslot')),
                ('requested_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='tutoring_reschedule_requests_made', to=settings.AUTH_USER_MODEL)),
                ('responded_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='tutoring_reschedule_requests_answered', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-requested_at'],
            },
        ),
    ]
