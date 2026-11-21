"""Tests for the login study reminder notification: on login a
student is reminded of the words, sentences and expressions studied
since their previous login, plus their overall progress so far."""

from datetime import timedelta

from django.core.cache import cache
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from account.models import CustomUser, Notification
from student.models import LearnedItem
from student.study_reminder import REMINDER_TITLE
from teacher.models import Idiom, Sentence, Vocabulary

PASSWORD = 'Study' + 'Reminder' + '#42'


def _student(email='learner@example.com'):
    return CustomUser.objects.create_user(
        email, PASSWORD, first_name='Pat', last_name='Student')


def _learned(student, when, **kwargs):
    item = LearnedItem.objects.create(student=student, **kwargs)
    LearnedItem.objects.filter(pk=item.pk).update(learned_at=when)
    return item


class StudyReminderLoginTests(TestCase):
    def setUp(self):
        cache.clear()
        self.user = _student()
        self.url = reverse('my_login')
        self.word = Vocabulary.objects.create(
            word='朋友', pinyin='péngyou', meaning='friend', level='level1')
        self.other_word = Vocabulary.objects.create(
            word='老師', pinyin='lǎoshī', meaning='teacher', level='level1')
        self.sentence = Sentence.objects.create(
            text='你好嗎？', translation='How are you?', level='level1')
        self.idiom = Idiom.objects.create(
            idiom='學中文', pinyin='xué zhōngwén',
            meaning='to learn Chinese', level='level1')
        two_days_ago = timezone.now() - timedelta(days=2)
        CustomUser.objects.filter(pk=self.user.pk).update(
            last_login=two_days_ago)

    def tearDown(self):
        cache.clear()

    def _login(self):
        return self.client.post(
            self.url, {'username': self.user.email, 'password': PASSWORD})

    def _reminders(self):
        return Notification.objects.filter(
            user=self.user, title=REMINDER_TITLE)

    def test_login_recaps_last_session_and_progress(self):
        yesterday = timezone.now() - timedelta(days=1)
        _learned(self.user, yesterday, vocabulary=self.word)
        _learned(self.user, yesterday, sentence=self.sentence)
        _learned(self.user, yesterday, idiom=self.idiom)

        response = self._login()
        self.assertEqual(response.status_code, 302)

        self.assertEqual(self._reminders().count(), 1)
        message = self._reminders().first().message
        self.assertIn('朋友', message)
        self.assertIn('你好嗎？', message)
        self.assertIn('學中文', message)
        self.assertIn('Words (1):', message)
        self.assertIn('Sentences (1):', message)
        self.assertIn('Expressions (1):', message)
        # 3 learned of 4 visible level-1 materials (2 words, 1 sentence,
        # 1 expression) = 75%.
        self.assertIn('3 of 4 materials learned (75%)', message)
        self.assertIn('1 words · 1 sentences · 1 expressions', message)

    def test_items_from_before_the_previous_login_are_not_repeated(self):
        three_days_ago = timezone.now() - timedelta(days=3)
        _learned(self.user, three_days_ago, vocabulary=self.word)
        self._login()
        self.assertEqual(self._reminders().count(), 0)

    def test_login_without_any_study_creates_no_reminder(self):
        self._login()
        self.assertEqual(self._reminders().count(), 0)

    def test_first_ever_login_creates_no_reminder(self):
        CustomUser.objects.filter(pk=self.user.pk).update(last_login=None)
        yesterday = timezone.now() - timedelta(days=1)
        _learned(self.user, yesterday, vocabulary=self.word)
        self._login()
        self.assertEqual(self._reminders().count(), 0)

    def test_second_login_without_new_study_does_not_duplicate(self):
        yesterday = timezone.now() - timedelta(days=1)
        _learned(self.user, yesterday, vocabulary=self.word)
        self._login()
        self.assertEqual(self._reminders().count(), 1)
        self.client.logout()
        self._login()
        self.assertEqual(self._reminders().count(), 1)

    def test_new_study_is_recapped_at_the_next_login(self):
        yesterday = timezone.now() - timedelta(days=1)
        _learned(self.user, yesterday, vocabulary=self.word)
        self._login()
        self.client.logout()
        _learned(self.user, timezone.now(), vocabulary=self.other_word)
        self._login()
        self.assertEqual(self._reminders().count(), 2)
        latest = self._reminders().order_by('-created_at').first()
        self.assertIn('老師', latest.message)
        self.assertIn('Words (1):', latest.message)
        self.assertNotIn('朋友', latest.message.split('progress so far')[0])
