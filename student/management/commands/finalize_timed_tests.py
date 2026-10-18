from django.core.management.base import BaseCommand
from django.utils import timezone
from student.models import TimedTestAttempt
from student.timed_tests import finalize_attempt


class Command(BaseCommand):
    help = 'Finalize expired timed tests, including when the student closed their browser.'

    def handle(self, *args, **options):
        ids = list(TimedTestAttempt.objects.filter(
            completed_at__isnull=True, deadline__lte=timezone.now()
        ).values_list('pk', flat=True))
        for attempt_id in ids:
            finalize_attempt(attempt_id, auto=True)
        self.stdout.write(f'Finalized {len(ids)} expired timed test attempts.')
