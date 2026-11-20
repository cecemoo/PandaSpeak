"""Tests that registering emails the PandaSpeak support inbox, and
that a failure of that notification can never break the signup.

These exercise the LIVE registration view
(account.email_verification_views.register), which creates the account
inactive and sends the user a verification email.
"""
from unittest.mock import patch

from django.core import mail
from django.core.mail import send_mail as real_send_mail
from django.test import TestCase
from django.urls import reverse

from account.models import CustomUser

FORM_DATA = {
    'email': 'newstudent@example.com',
    'first_name': 'New',
    'last_name': 'Student',
    'password1': 'Str0ng!Passw0rd',
    'password2': 'Str0ng!Passw0rd',
}


def _support_messages():
    return [m for m in mail.outbox if m.to == ['pandaspeaksupport@gmail.com']]


class RegistrationNotificationTests(TestCase):
    def test_registration_emails_support_inbox(self):
        response = self.client.post(reverse('register'), FORM_DATA)
        self.assertEqual(response.status_code, 200)  # "verification sent" page
        user = CustomUser.objects.get(email='newstudent@example.com')
        self.assertFalse(user.is_active)  # awaiting email verification
        support = _support_messages()
        self.assertEqual(len(support), 1)
        self.assertEqual(support[0].subject, 'New PandaSpeak Account Registration')
        self.assertIn('newstudent@example.com', support[0].body)
        self.assertIn('Student', support[0].body)
        # The user still gets their own verification email too.
        user_mail = [m for m in mail.outbox if m.to == ['newstudent@example.com']]
        self.assertEqual(len(user_mail), 1)

    def test_support_email_failure_does_not_break_registration(self):
        def flaky_send_mail(**kwargs):
            if kwargs.get('recipient_list') == ['pandaspeaksupport@gmail.com']:
                raise RuntimeError('SMTP down')
            return real_send_mail(**kwargs)

        with patch('account.email_verification_views.send_mail',
                   side_effect=flaky_send_mail):
            response = self.client.post(reverse('register'), FORM_DATA)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(CustomUser.objects.filter(
            email='newstudent@example.com').exists())
