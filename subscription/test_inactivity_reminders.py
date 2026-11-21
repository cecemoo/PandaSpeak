"""Tests for send_inactivity_reminders: students who have not logged
in for over 5 days get one email per inactivity spell, recapping
their last studied items and overall progress."""

from datetime import timedelta

from django.core import mail
from django.core.management import call_command
from django.test import TestCase
from django.utils import timezone

from account.models import CustomUser, Notification
from student.models import LearnedItem
from subscription.management.commands.send_inactivity_reminders import (
    REMINDER_TITLE,
)
from teacher.models import Vocabulary

PASSWORD = 'Inactivity' + 'Test' + '#42'


def _user(email, days_since_login=None, **flags):
    user = CustomUser.objects.create_user(
        email, PASSWORD, first_name='Pat', last_name='Student', **flags)
    if days_since_login is not None:
        CustomUser.objects.filter(pk=user.pk).update(
            last_login=timezone.now() - timedelta(days=days_since_login))
        user.refresh_from_db()
    return user


class InactivityReminderTests(TestCase):
    def setUp(self):
        self.word = Vocabulary.objects.create(
            word='朋友', pinyin='péngyou', meaning='friend', level='level1')

    def _run(self):
        call_command('send_inactivity_reminders')

    def test_inactive_student_gets_email_with_recap_and_progress(self):
        user = _user('away@example.com', days_since_login=6)
        LearnedItem.objects.create(student=user, vocabulary=self.word)

        self._run()

        self.assertEqual(len(mail.outbox), 1)
        email = mail.outbox[0]
        self.assertEqual(email.to, ['away@example.com'])
        self.assertEqual(email.subject, REMINDER_TITLE)
        self.assertIn('朋友', email.body)
        self.assertIn('Last time you studied:', email.body)
        self.assertIn('1 of 1 materials learned (100%)', email.body)
        self.assertIn('https://pandaspeak.org/my_login/', email.body)
        self.assertTrue(
            Notification.objects.filter(
                user=user, title=REMINDER_TITLE).exists())

    def test_recently_active_student_gets_no_email(self):
        _user('active@example.com', days_since_login=2)
        self._run()
        self.assertEqual(len(mail.outbox), 0)

    def test_four_days_away_gets_no_email(self):
        _user('four@example.com', days_since_login=4)
        self._run()
        self.assertEqual(len(mail.outbox), 0)

    def test_one_email_per_inactivity_spell(self):
        _user('away2@example.com', days_since_login=6)
        self._run()
        self._run()
        self.assertEqual(len(mail.outbox), 1)

    def test_new_spell_after_returning_gets_a_new_email(self):
        user = _user('boomerang@example.com', days_since_login=6)
        old = Notification.objects.create(
            user=user, title=REMINDER_TITLE, message='earlier nudge')
        Notification.objects.filter(pk=old.pk).update(
            created_at=timezone.now() - timedelta(days=10))

        self._run()
        self.assertEqual(len(mail.outbox), 1)

    def test_teacher_staff_and_never_logged_in_are_excluded(self):
        _user('teacher@example.com', days_since_login=9, is_teacher=True)
        _user('staff@example.com', days_since_login=9, is_staff=True)
        _user('never@example.com', days_since_login=None)
        _user('unverified@example.com', days_since_login=9, is_active=False)
        self._run()
        self.assertEqual(len(mail.outbox), 0)

    def test_inactive_student_without_study_history_still_emailed(self):
        _user('newbie@example.com', days_since_login=7)
        self._run()
        self.assertEqual(len(mail.outbox), 1)
        self.assertNotIn('Last time you studied:', mail.outbox[0].body)
        self.assertIn(
            'https://pandaspeak.org/my_login/', mail.outbox[0].body)
