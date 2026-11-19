"""Tests for the login brute-force throttle and password policy."""
from django.contrib.auth.password_validation import validate_password
from django.core.cache import cache
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.urls import reverse

from account.models import CustomUser

GOOD_PASSWORD = 'Str0ng!Passw0rd'


def _user(email):
    return CustomUser.objects.create_user(
        email=email, password=GOOD_PASSWORD, first_name='Pat', last_name='Student')


class LoginThrottleTests(TestCase):
    def setUp(self):
        cache.clear()
        self.user = _user('victim@example.com')
        self.url = reverse('my_login')

    def tearDown(self):
        cache.clear()

    def _attempt(self, email, password):
        return self.client.post(self.url, {'username': email, 'password': password})

    def test_correct_login_still_works(self):
        response = self._attempt('victim@example.com', GOOD_PASSWORD)
        self.assertEqual(response.status_code, 302)

    def test_five_failures_block_even_the_correct_password(self):
        for _ in range(5):
            response = self._attempt('victim@example.com', 'wrong-password')
            self.assertEqual(response.status_code, 200)
        response = self._attempt('victim@example.com', GOOD_PASSWORD)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Too many failed login attempts')

    def test_blocking_one_account_does_not_block_another(self):
        _user('other@example.com')
        for _ in range(5):
            self._attempt('victim@example.com', 'wrong-password')
        response = self._attempt('other@example.com', GOOD_PASSWORD)
        self.assertEqual(response.status_code, 302)

    def test_successful_login_clears_the_failure_counter(self):
        for _ in range(4):
            self._attempt('victim@example.com', 'wrong-password')
        response = self._attempt('victim@example.com', GOOD_PASSWORD)
        self.assertEqual(response.status_code, 302)
        self.client.logout()
        for _ in range(4):
            self._attempt('victim@example.com', 'wrong-password')
        response = self._attempt('victim@example.com', GOOD_PASSWORD)
        self.assertEqual(response.status_code, 302)


class PasswordPolicyTests(TestCase):
    def test_minimum_length_is_ten(self):
        with self.assertRaises(ValidationError):
            validate_password('Ab1!xyz78')  # 9 characters

    def test_common_password_rejected(self):
        with self.assertRaises(ValidationError):
            validate_password('password1234')

    def test_strong_password_accepted(self):
        validate_password(GOOD_PASSWORD)  # should not raise
