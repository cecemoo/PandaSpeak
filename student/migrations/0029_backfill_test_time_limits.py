from django.db import migrations


def backfill_time_limits(apps, schema_editor):
    # Cece's instruction (2026-11-03): all tests should be timed. Tests
    # without an instructor-set limit get the 30-minute default, matching
    # DEFAULT_TEST_TIME_LIMIT_MINUTES in student/models.py.
    LanguageTest = apps.get_model('student', 'LanguageTest')
    LanguageTest.objects.filter(time_limit_minutes__isnull=True).update(
        time_limit_minutes=30
    )


class Migration(migrations.Migration):

    dependencies = [
        ('student', '0028_assessmentrequest_and_more'),
    ]

    operations = [
        migrations.RunPython(backfill_time_limits, migrations.RunPython.noop),
    ]
