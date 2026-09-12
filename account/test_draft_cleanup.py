from datetime import timedelta
from unittest.mock import patch
from django.core.management import call_command
from django.test import TestCase
from django.utils import timezone
from account.models import Announcement, AnnouncementDelivery, CustomUser


class DraftCleanupTests(TestCase):
    def test_expiry_boundary_and_queued_protection(self):
        user = CustomUser.objects.create_user('test@example.com', 'test')
        now = timezone.now()
        def make(age, queued=False):
            item = Announcement.objects.create(subject='Test', body='Test', created_by=user, queued_at=now if queued else None)
            Announcement.objects.filter(pk=item.pk).update(created_at=now-age)
            return item.pk
        expired = make(timedelta(days=4))
        boundary = make(timedelta(days=3))
        recent = make(timedelta(days=3)-timedelta(seconds=1))
        queued = make(timedelta(days=4), True)
        has_delivery = make(timedelta(days=4))
        AnnouncementDelivery.objects.create(announcement_id=has_delivery, user=user)
        with patch('account.management.commands.delete_expired_announcement_drafts.timezone.now', return_value=now):
            call_command('delete_expired_announcement_drafts')
            call_command('delete_expired_announcement_drafts')
        self.assertSetEqual(set(Announcement.objects.values_list('pk', flat=True)), {recent, queued, has_delivery})
