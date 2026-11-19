"""End-to-end tests for the password reset flow, including resetting
while the login throttle is active after failed attempts."""
import re

from django.core import mail
from django.core.cache import cache
from django.test import TestCase
from django.urls import reverse

from account.models import CustomUser

OLD_PASSWORD = 'Old!Passw0rd99'
NEW_PASSWORD = 'New!Passw0rd99'


class PasswordResetFlowTests(TestCase):
    def setUp(self):
        cache.clear()
        self.user = CustomUser.objects.create_user(
            email='resetme@example.com', password=OLD_PASSWORD,
            first_name='Re', last_name='Setter')

    def tearDown(self):
        cache.clear()

    def _request_reset_and_get_link(self):
        response = self.client.post(
            reverse('password_reset'), {'email': 'resetme@example.com'})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(len(mail.outbox), 1)
        match = re.search(r'/password-reset-confirm/\S+', mail.outbox[0].body)
        self.assertIsNotNone(match)
        return match.group(0)

    def _complete_reset(self, link, new_password):
        response = self.client.get(link)
        self.assertEqual(response.status_code, 302)  # token -> session handoff
        return self.client.post(response.url, {
            'new_password1': new_password, 'new_password2': new_password})

    def _login(self, password):
        return self.client.post(reverse('my_login'), {
            'username': 'resetme@example.com', 'password': password})

    def test_forgot_password_full_flow(self):
        link = self._request_reset_and_get_link()
        response = self._complete_reset(link, NEW_PASSWORD)
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse('password_reset_complete'), response.url)
        self.assertEqual(self._login(OLD_PASSWORD).status_code, 200)
        self.assertEqual(self._login(NEW_PASSWORD).status_code, 302)

    def test_reset_while_throttled_then_login_immediately(self):
        # Five failed attempts trigger the throttle.
        for _ in range(5):
            self._login('wrong-password')
        blocked = self._login(OLD_PASSWORD)
        self.assertEqual(blocked.status_code, 200)
        self.assertContains(blocked, 'Too many failed login attempts')
        self.assertContains(blocked, 'Forgot your password?')
        # The reset flow itself is never throttled...
        link = self._request_reset_and_get_link()
        response = self._complete_reset(link, NEW_PASSWORD)
        self.assertEqual(response.status_code, 302)
        # ...and a successful reset lifts the pause right away.
        self.assertEqual(self._login(NEW_PASSWORD).status_code, 302)

    def test_reset_enforces_minimum_password_length(self):
        link = self._request_reset_and_get_link()
        response = self.client.get(link)
        response = self.client.post(response.url, {
            'new_password1': 'Ab1!xyz78', 'new_password2': 'Ab1!xyz78'})  # 9 chars
        self.assertEqual(response.status_code, 200)  # form error, not saved
        self.assertEqual(self._login(OLD_PASSWORD).status_code, 302)
