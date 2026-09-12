from unittest.mock import patch
from datetime import timedelta
from django.http import HttpResponse
from django.test import TestCase
from django.utils import timezone
from account.models import CustomUser, Announcement


class AnnouncementFeedTests(TestCase):
    @patch('account.announcement_views.render', return_value=HttpResponse('ok'))
    def test_latest_three_published_for_students_and_teachers(self, render):
        manager = CustomUser.objects.create_user('manager@example.com', 'test', is_staff=True)
        user = CustomUser.objects.create_user('user@example.com', 'test')
        now = timezone.now()
        ids = []
        for i in range(4):
            item = Announcement.objects.create(subject=str(i), body='Update', created_by=manager, queued_at=now + timedelta(minutes=i))
            ids.append(item.pk)
        Announcement.objects.create(subject='Private draft', body='Private', created_by=manager)
        for teacher in [False, True]:
            for opted_in in [False, True]:
                user.is_teacher = teacher
                user.news_emails = opted_in
                user.save()
                self.client.force_login(user)
                self.client.get('/preferences/')
                items = render.call_args.args[2]['announcements']
                self.assertEqual(list(items.values_list('pk', flat=True)), ids[::-1][:3])
        self.client.force_login(manager)
        response = self.client.get('/preferences/')
        self.assertEqual(response.url, '/manager/')
