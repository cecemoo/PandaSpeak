import re

from django.core import mail
from django.test import TestCase
from django.urls import reverse

from .models import CustomUser


def _verify_emails():
    return [m for m in mail.outbox if m.subject == 'Verify Your PandaSpeak Email']


class ResendVerificationTests(TestCase):
    def _register(self, email):
        resp = self.client.post(reverse('register'), {
            'email': email,
            'first_name': 'Resend',
            'last_name': 'Tester',
            'password1': 'Str0ng!Passw0rd',
            'password2': 'Str0ng!Passw0rd',
        })
        self.assertEqual(resp.status_code, 200)

    def test_form_page_loads(self):
        resp = self.client.get(reverse('resend_verification'))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'name="email"')

    def test_resend_sends_fresh_link_that_verifies(self):
        self._register('resend1@example.com')
        self.assertEqual(len(_verify_emails()), 1)

        resp = self.client.post(reverse('resend_verification'),
                                {'email': 'resend1@example.com'})
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'waiting for verification')
        emails = _verify_emails()
        self.assertEqual(len(emails), 2)
        self.assertEqual(emails[-1].to, ['resend1@example.com'])

        path = re.search(r'/verify-email/\S+', emails[-1].body).group(0)
        resp = self.client.get(path)
        self.assertEqual(resp.status_code, 302)
        user = CustomUser.objects.get(email='resend1@example.com')
        self.assertTrue(user.is_active)

    def test_resend_for_active_user_sends_nothing(self):
        self._register('resend2@example.com')
        user = CustomUser.objects.get(email='resend2@example.com')
        user.is_active = True
        user.save(update_fields=['is_active'])
        mail.outbox.clear()

        resp = self.client.post(reverse('resend_verification'),
                                {'email': 'resend2@example.com'})
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'waiting for verification')
        self.assertEqual(len(_verify_emails()), 0)

    def test_resend_for_unknown_email_sends_nothing(self):
        resp = self.client.post(reverse('resend_verification'),
                                {'email': 'nobody-here@example.com'})
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'waiting for verification')
        self.assertEqual(len(_verify_emails()), 0)

    def test_resend_is_rate_limited_per_email(self):
        self._register('resend3@example.com')
        self.assertEqual(len(_verify_emails()), 1)
        for _ in range(3):
            self.client.post(reverse('resend_verification'),
                             {'email': 'resend3@example.com'})
        self.assertEqual(len(_verify_emails()), 4)
        # Fourth resend within the hour sends nothing.
        self.client.post(reverse('resend_verification'),
                         {'email': 'resend3@example.com'})
        self.assertEqual(len(_verify_emails()), 4)
