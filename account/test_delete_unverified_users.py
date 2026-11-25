"""Tests for the delete_unverified_users management command."""
from datetime import timedelta
from decimal import Decimal
from io import StringIO

from django.core.management import call_command
from django.test import TestCase
from django.utils import timezone

from account.models import CustomUser
from subscription.models import Subscription


def _user(email, *, active=False, joined_days_ago=3, last_login=None, **flags):
    user = CustomUser.objects.create_user(
        email=email, password='<redacted>', first_name='Test', last_name='User')
    user.is_active = active
    user.last_login = last_login
    for name, value in flags.items():
        setattr(user, name, value)
    user.save()
    # date_joined is auto-set; move it into the past directly.
    CustomUser.objects.filter(pk=user.pk).update(
        date_joined=timezone.now() - timedelta(days=joined_days_ago))
    user.refresh_from_db()
    return user


def _run():
    out = StringIO()
    call_command('delete_unverified_users', stdout=out)
    return out.getvalue()


class DeleteUnverifiedUsersTests(TestCase):
    def test_old_unverified_empty_account_is_deleted(self):
        _user('junk@example.com', joined_days_ago=3)
        result = _run()
        self.assertIn('Deleted 1 unverified account(s).', result)
        self.assertFalse(CustomUser.objects.filter(email='junk@example.com').exists())

    def test_recent_unverified_account_is_kept(self):
        _user('new@example.com', joined_days_ago=0)
        result = _run()
        self.assertIn('Deleted 0 unverified account(s).', result)
        self.assertTrue(CustomUser.objects.filter(email='new@example.com').exists())

    def test_verified_account_is_kept(self):
        _user('real@example.com', active=True, joined_days_ago=30,
              last_login=timezone.now())
        _run()
        self.assertTrue(CustomUser.objects.filter(email='real@example.com').exists())

    def test_unverified_account_with_subscription_is_kept(self):
        user = _user('school@example.com', joined_days_ago=3)
        Subscription.objects.create(
            user=user, subscription_plan='Base',
            subscription_cost=Decimal('15.00'), is_active=True)
        _run()
        self.assertTrue(CustomUser.objects.filter(email='school@example.com').exists())

    def test_staff_and_teacher_shells_are_kept(self):
        _user('staff@example.com', joined_days_ago=30, is_staff=True)
        _user('teacher@example.com', joined_days_ago=30, is_teacher=True)
        _run()
        self.assertTrue(CustomUser.objects.filter(email='staff@example.com').exists())
        self.assertTrue(CustomUser.objects.filter(email='teacher@example.com').exists())
