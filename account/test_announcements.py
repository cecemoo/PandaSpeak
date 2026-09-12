from unittest.mock import patch
from django.core import mail, signing
from django.core.management import call_command
from django.http import HttpResponse
from django.test import TestCase
from .models import CustomUser, Announcement, AnnouncementDelivery


class AnnouncementTests(TestCase):
    def setUp(self):
        self.manager = CustomUser.objects.create_user('manager@example.com', 'test', is_staff=True)
        self.user = CustomUser.objects.create_user('student@example.com', 'test')
        self.item = Announcement.objects.create(subject='News', body='Hello', created_by=self.manager)

    def test_default_opt_out(self):
        self.assertFalse(self.user.news_emails)

    def test_preference_dashboard_redirects(self):
        for fields, target in [({}, '/student/'), ({'is_teacher': True}, '/teacher/'), ({'is_staff': True}, '/manager/')]:
            for name, value in fields.items():
                setattr(self.user, name, value)
            self.user.save()
            self.client.force_login(self.user)
            for data in [{'news_emails': 'on'}, {}]:
                response = self.client.post('/preferences/', data)
                self.assertEqual(response.status_code, 302)
                self.assertEqual(response.url, target)

    @patch('account.announcement_views.render', return_value=HttpResponse('ok'))
    def test_preference_page_reflects_saved_status(self, render):
        self.client.force_login(self.user)
        for opted_in in [True, False]:
            CustomUser.objects.filter(pk=self.user.pk).update(news_emails=opted_in)
            self.client.get('/preferences/')
            self.assertEqual(render.call_args.args[1], 'account/email_preferences.html')
            self.assertEqual(render.call_args.args[2]['opted_in'], opted_in)

    def test_preference_choice(self):
        self.client.force_login(self.user)
        self.client.post('/preferences/', {'news_emails': 'on'})
        self.user.refresh_from_db()
        self.assertTrue(self.user.news_emails)
        self.client.post('/preferences/', {})
        self.user.refresh_from_db()
        self.assertFalse(self.user.news_emails)

    def test_manager_only_and_queue_once(self):
        self.client.force_login(self.user)
        self.assertEqual(self.client.post(f'/announcements/{self.item.pk}/', {'confirm': 'yes'}).status_code, 302)
        self.assertFalse(AnnouncementDelivery.objects.exists())
        self.user.news_emails = True
        self.user.save()
        self.client.force_login(self.manager)
        for _ in range(2):
            self.client.post(f'/announcements/{self.item.pk}/', {'confirm': 'yes'})
        self.assertEqual(AnnouncementDelivery.objects.count(), 1)

    def test_delivery_rechecks_consent_and_does_not_repeat(self):
        delivery = AnnouncementDelivery.objects.create(announcement=self.item, user=self.user)
        call_command('send_news_announcements')
        self.assertEqual(len(mail.outbox), 0)
        delivery.refresh_from_db()
        self.assertEqual(delivery.status, 'skipped')
        self.user.news_emails = True
        self.user.save()
        delivery.status = 'pending'
        delivery.save()
        call_command('send_news_announcements')
        call_command('send_news_announcements')
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, [self.user.email])
        self.assertIn('Unsubscribe:', mail.outbox[0].body)

    @patch('account.announcement_views.render', return_value=HttpResponse('ok'))
    def test_unsubscribe_confirmation(self, render):
        self.user.news_emails = True
        self.user.save()
        token = signing.dumps(self.user.pk, salt='pandaspeak-news')
        self.client.get(f'/unsubscribe/{token}/')
        self.user.refresh_from_db()
        self.assertTrue(self.user.news_emails)
        self.client.post(f'/unsubscribe/{token}/')
        self.user.refresh_from_db()
        self.assertFalse(self.user.news_emails)

    def test_failed_send_not_retried(self):
        self.user.news_emails = True
        self.user.save()
        delivery = AnnouncementDelivery.objects.create(announcement=self.item, user=self.user)
        with patch('django.core.mail.EmailMessage.send', side_effect=RuntimeError('test')) as send:
            call_command('send_news_announcements')
            call_command('send_news_announcements')
        self.assertEqual(send.call_count, 1)
        delivery.refresh_from_db()
        self.assertEqual(delivery.status, 'failed')
