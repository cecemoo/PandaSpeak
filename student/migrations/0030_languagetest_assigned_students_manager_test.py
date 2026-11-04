# Replaces LanguageTest.assigned_student (FK) with assigned_students (M2M)
# so a test can be assigned to several students, and adds is_manager_test.
# The unrelated AIConversationUsage index renames makemigrations tried to
# bundle in are pre-existing Django-version drift noise and are excluded,
# as in migration 0028.

from django.conf import settings
from django.db import migrations, models


def copy_assigned_student_forward(apps, schema_editor):
    LanguageTest = apps.get_model('student', 'LanguageTest')
    for test in LanguageTest.objects.exclude(assigned_student__isnull=True):
        test.assigned_students.add(test.assigned_student)


def copy_assigned_student_backward(apps, schema_editor):
    LanguageTest = apps.get_model('student', 'LanguageTest')
    for test in LanguageTest.objects.all():
        first = test.assigned_students.order_by('id').first()
        if first is not None:
            test.assigned_student = first
            test.save(update_fields=['assigned_student'])


class Migration(migrations.Migration):

    dependencies = [
        ('student', '0029_backfill_test_time_limits'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='languagetest',
            name='assigned_students',
            field=models.ManyToManyField(blank=True, related_name='assigned_tests', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='languagetest',
            name='is_manager_test',
            field=models.BooleanField(default=False),
        ),
        migrations.RunPython(copy_assigned_student_forward, copy_assigned_student_backward),
        migrations.RemoveField(
            model_name='languagetest',
            name='assigned_student',
        ),
    ]
