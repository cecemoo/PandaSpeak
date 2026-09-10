from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('course', '0005_studentgroup'),
    ]

    operations = [
        migrations.AddField(
            model_name='booking',
            name='meeting_room_id',
            field=models.CharField(blank=True, max_length=120, null=True, unique=True),
        ),
        migrations.AddField(
            model_name='booking',
            name='payout_eligible_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='booking',
            name='payout_status',
            field=models.CharField(
                choices=[
                    ('pending', 'Pending'),
                    ('awaiting_release', 'Awaiting Release'),
                    ('on_hold', 'On Hold'),
                    ('transferred', 'Transferred'),
                    ('reversed', 'Reversed'),
                ],
                default='pending',
                max_length=20,
            ),
        ),
        migrations.AddField(
            model_name='booking',
            name='session_completed_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='booking',
            name='session_started_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='booking',
            name='session_status',
            field=models.CharField(
                choices=[
                    ('scheduled', 'Scheduled'),
                    ('in_progress', 'In Progress'),
                    ('completed', 'Completed'),
                    ('review_required', 'Review Required'),
                    ('disputed', 'Disputed'),
                    ('no_show_student', 'Student No-show'),
                    ('no_show_teacher', 'Teacher No-show'),
                ],
                default='scheduled',
                max_length=30,
            ),
        ),
        migrations.AddField(
            model_name='booking',
            name='shared_minutes',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='booking',
            name='student_reported_issue',
            field=models.BooleanField(default=False),
        ),
        migrations.CreateModel(
            name='SessionAttendance',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('joined_at', models.DateTimeField(auto_now_add=True)),
                ('last_seen_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('left_at', models.DateTimeField(blank=True, null=True)),
                ('booking', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='attendance_records', to='course.booking')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='tutoring_attendance_records', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['joined_at'],
            },
        ),
        migrations.AddIndex(
            model_name='booking',
            index=models.Index(fields=['session_status', 'payout_status'], name='course_book_session_5bd7e8_idx'),
        ),
        migrations.AddIndex(
            model_name='sessionattendance',
            index=models.Index(fields=['booking', 'user', 'joined_at'], name='course_sess_booking_4dad75_idx'),
        ),
    ]
