from datetime import timedelta

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from account.models import Announcement


class Command(BaseCommand):
    help = 'Permanently delete unqueued announcement drafts 72 hours after creation.'

    def handle(self, *args, **options):
        cutoff = timezone.now() - timedelta(days=3)
        ids = Announcement.objects.filter(queued_at__isnull=True, created_at__lte=cutoff).values_list('pk', flat=True)
        count = 0
        for pk in ids.iterator():
            # Use the same row lock as publication; never delete a queued announcement.
            with transaction.atomic():
                draft = Announcement.objects.select_for_update().filter(pk=pk, queued_at__isnull=True, created_at__lte=cutoff).first()
                if draft is not None and not draft.deliveries.exists():
                    draft.delete()
                    count += 1
        self.stdout.write(f'Deleted {count} expired announcement draft(s).')
