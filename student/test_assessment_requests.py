"""Tests for comprehensive assessment requests from the Test List page.

Covers Cece's 2026-11-03 spec (revised the same day): every assessment —
listening, speaking, and speaking & listening — is generated instantly
from the chosen level's materials and assigned to the requesting student
only. A generated speaking/mixed test records its AssessmentRequest as
fulfilled, linked to the test. When a level lacks the material for
instant generation, a speaking/mixed request falls back to a pending
AssessmentRequest with an email alert to the support inbox; pending
requests can be cancelled by their owner.
"""
from decimal import Decimal

from django.core import mail
from django.test import TestCase
from django.urls import reverse

from account.models import CustomUser
from subscription.models import Subscription
from teacher.models import Vocabulary

from django.utils import timezone

from .models import (AssessmentRequest, DEFAULT_TEST_TIME_LIMIT_MINUTES,
                     LanguageTest, TimedTestAttempt)


def _subscriber(email, first_name='Pat'):
    user = CustomUser.objects.create_user(
        email=email, password='<redacted>', first_name=first_name, last_name='Student')
    Subscription.objects.create(
        user=user, subscription_plan='Base', subscription_cost=Decimal('15.00'), is_active=True)
    return user


def _vocabulary(word, translation, level='level1', audio=None):
    return Vocabulary.objects.create(
        word=word,
        meaning=f'meaning of {word}',
        english_translation=translation,
        audio_file=audio or f'vocab/{word}.mp3',
        level=level,
    )


class ListeningAssessmentGenerationTests(TestCase):
    def setUp(self):
        self.student = _subscriber('student@example.com', 'Sue')
        self.other = _subscriber('other@example.com', 'Omar')
        self.translations = {}
        for i in range(12):
            item = _vocabulary(f'word-{i}', f'translation {i}')
            self.translations[item.english_translation] = item.audio_file.name

    def _request(self, user, **overrides):
        data = {'level': 'level1', 'test_type': 'listening'}
        data.update(overrides)
        self.client.force_login(user)
        return self.client.post(reverse('request_assessment'), data)

    def test_listening_request_generates_assigned_test(self):
        response = self._request(self.student)
        test = LanguageTest.objects.get(assigned_students=self.student)
        self.assertEqual(test.test_type, 'listening')
        self.assertEqual(test.level, 'Level I')
        self.assertEqual(test.title, 'Level I Listening Assessment')
        self.assertTrue(test.is_active)
        self.assertTrue(test.is_published)
        self.assertRedirects(response, reverse('take_test', args=[test.id]))

        questions = list(test.questions.order_by('order'))
        self.assertGreaterEqual(len(questions), 10)
        self.assertEqual(len(questions), 12)
        for index, question in enumerate(questions, start=1):
            self.assertEqual(question.order, index)
            self.assertEqual(question.question_type, 'listen_mc')
            self.assertEqual(question.points, 1)
            choices = {
                'A': question.choice_a, 'B': question.choice_b,
                'C': question.choice_c, 'D': question.choice_d,
            }
            self.assertEqual(len(set(choices.values())), 4)
            for text in choices.values():
                self.assertIn(text, self.translations)
            correct_text = choices[question.correct_answer]
            # The audio must be the source recording of the correct item.
            self.assertEqual(question.audio.name, self.translations[correct_text])

    def test_generated_test_visible_only_to_its_student(self):
        self._request(self.student)
        test = LanguageTest.objects.get(assigned_students=self.student)

        self.client.force_login(self.student)
        response = self.client.get(reverse('test_list'))
        self.assertIn(test, list(response.context['tests']))
        response = self.client.get(reverse('take_test', args=[test.id]))
        self.assertEqual(response.status_code, 200)

        self.client.force_login(self.other)
        response = self.client.get(reverse('test_list'))
        self.assertNotIn(test, list(response.context['tests']))
        response = self.client.get(reverse('take_test', args=[test.id]))
        self.assertEqual(response.status_code, 404)

    def test_second_listening_request_reuses_open_test(self):
        first = self._request(self.student)
        test = LanguageTest.objects.get(assigned_students=self.student)
        second = self._request(self.student)
        self.assertEqual(LanguageTest.objects.count(), 1)
        self.assertRedirects(first, reverse('take_test', args=[test.id]))
        self.assertRedirects(second, reverse('take_test', args=[test.id]))

    def test_insufficient_material_creates_nothing(self):
        # A different level with only a handful of items cannot reach the
        # 10-question minimum.
        for i in range(5):
            _vocabulary(f'sparse-{i}', f'sparse translation {i}', level='level2')
        self.client.force_login(self.student)
        response = self.client.post(
            reverse('request_assessment'),
            {'level': 'level2', 'test_type': 'listening'},
            follow=True)
        self.assertEqual(LanguageTest.objects.count(), 0)
        self.assertContains(
            response,
            'There is not enough listening material at that level yet '
            'to build an assessment.')


class SpeakingAssessmentGenerationTests(TestCase):
    """Cece's revised spec (2026-11-03): speaking and mixed assessments
    are generated instantly, just like listening ones. The request is
    recorded already fulfilled, linked to the generated test, and no
    support email is sent on the instant path."""

    def setUp(self):
        self.student = _subscriber('student@example.com', 'Sue')
        self.other = _subscriber('other@example.com', 'Omar')
        self.words = set()
        for i in range(12):
            item = _vocabulary(f'word-{i}', f'translation {i}', level='level2')
            self.words.add(item.word)

    def _request(self, user, **overrides):
        data = {'level': 'level2', 'test_type': 'speaking'}
        data.update(overrides)
        self.client.force_login(user)
        return self.client.post(reverse('request_assessment'), data)

    def _support_emails(self):
        # Creating a Subscription also sends the user mail (subscription
        # signals), so count only the alerts addressed to the support inbox.
        return [m for m in mail.outbox if m.to == ['pandaspeaksupport@gmail.com']]

    def test_speaking_request_generates_test_and_fulfilled_request(self):
        response = self._request(self.student)
        test = LanguageTest.objects.get(assigned_students=self.student)
        self.assertEqual(test.test_type, 'speaking')
        self.assertEqual(test.level, 'Level II')
        self.assertEqual(test.title, 'Level II Speaking Assessment')
        self.assertTrue(test.is_active)
        self.assertTrue(test.is_published)
        self.assertRedirects(response, reverse('take_test', args=[test.id]))

        questions = list(test.questions.order_by('order'))
        self.assertEqual(len(questions), 10)
        for index, question in enumerate(questions, start=1):
            self.assertEqual(question.order, index)
            self.assertEqual(question.question_type, 'speak_read')
            self.assertEqual(question.points, 1)
            self.assertIn(question.prompt, self.words)

        assessment_request = AssessmentRequest.objects.get(student=self.student)
        self.assertEqual(assessment_request.level, 'level2')
        self.assertEqual(assessment_request.test_type, 'speaking')
        self.assertEqual(assessment_request.status, 'fulfilled')
        self.assertEqual(assessment_request.fulfilled_test, test)
        self.assertEqual(self._support_emails(), [])

    def test_mixed_request_generates_listening_then_speaking(self):
        response = self._request(self.student, test_type='mixed')
        test = LanguageTest.objects.get(assigned_students=self.student)
        self.assertEqual(test.test_type, 'mixed')
        self.assertEqual(test.title, 'Level II Speaking & Listening Assessment')
        self.assertRedirects(response, reverse('take_test', args=[test.id]))

        questions = list(test.questions.order_by('order'))
        self.assertEqual(len(questions), 20)
        self.assertEqual([q.order for q in questions], list(range(1, 21)))
        for question in questions[:10]:
            self.assertEqual(question.question_type, 'listen_mc')
        for question in questions[10:]:
            self.assertEqual(question.question_type, 'speak_read')
            self.assertEqual(question.points, 1)
            self.assertIn(question.prompt, self.words)

        assessment_request = AssessmentRequest.objects.get(student=self.student)
        self.assertEqual(assessment_request.test_type, 'mixed')
        self.assertEqual(assessment_request.status, 'fulfilled')
        self.assertEqual(assessment_request.fulfilled_test, test)
        self.assertEqual(self._support_emails(), [])

    def test_second_speaking_request_reuses_open_test(self):
        first = self._request(self.student)
        test = LanguageTest.objects.get(assigned_students=self.student)
        second = self._request(self.student)
        self.assertEqual(LanguageTest.objects.count(), 1)
        self.assertEqual(AssessmentRequest.objects.count(), 1)
        self.assertRedirects(first, reverse('take_test', args=[test.id]))
        self.assertRedirects(second, reverse('take_test', args=[test.id]))

    def test_generated_speaking_test_visible_only_to_its_student(self):
        self._request(self.student)
        test = LanguageTest.objects.get(assigned_students=self.student)

        self.client.force_login(self.student)
        response = self.client.get(reverse('test_list'))
        self.assertIn(test, list(response.context['tests']))

        self.client.force_login(self.other)
        response = self.client.get(reverse('test_list'))
        self.assertNotIn(test, list(response.context['tests']))
        response = self.client.get(reverse('take_test', args=[test.id]))
        self.assertEqual(response.status_code, 404)


class SpeakingFallbackTests(TestCase):
    """When a level lacks the material for instant generation, speaking
    and mixed requests fall back to the original flow: a pending
    AssessmentRequest plus one email to the support inbox."""

    def setUp(self):
        self.student = _subscriber('student@example.com', 'Sue')
        # Only 4 items at Level III: too few distinct texts for the
        # 10 speaking prompts and too few answers for a 10-question
        # listening part.
        for i in range(4):
            _vocabulary(f'sparse-{i}', f'sparse translation {i}', level='level3')

    def _request(self, **overrides):
        data = {'level': 'level3', 'test_type': 'speaking'}
        data.update(overrides)
        self.client.force_login(self.student)
        return self.client.post(reverse('request_assessment'), data)

    def _support_emails(self):
        return [m for m in mail.outbox if m.to == ['pandaspeaksupport@gmail.com']]

    def test_insufficient_speaking_pool_falls_back_to_pending_request(self):
        response = self._request()
        self.assertRedirects(response, reverse('test_list'))
        self.assertEqual(LanguageTest.objects.count(), 0)
        assessment_request = AssessmentRequest.objects.get(student=self.student)
        self.assertEqual(assessment_request.level, 'level3')
        self.assertEqual(assessment_request.test_type, 'speaking')
        self.assertEqual(assessment_request.status, 'pending')
        self.assertIsNone(assessment_request.fulfilled_test)
        support_emails = self._support_emails()
        self.assertEqual(len(support_emails), 1)
        message = support_emails[0]
        self.assertIn('Level III', message.subject)
        self.assertIn('Speaking', message.subject)
        self.assertIn(self.student.email, message.body)

    def test_insufficient_material_mixed_request_also_falls_back(self):
        response = self._request(test_type='mixed')
        self.assertRedirects(response, reverse('test_list'))
        self.assertEqual(LanguageTest.objects.count(), 0)
        assessment_request = AssessmentRequest.objects.get(student=self.student)
        self.assertEqual(assessment_request.test_type, 'mixed')
        self.assertEqual(assessment_request.status, 'pending')
        self.assertEqual(len(self._support_emails()), 1)

    def test_duplicate_fallback_request_creates_no_second_record(self):
        self._request()
        self._request()
        self.assertEqual(AssessmentRequest.objects.count(), 1)
        self.assertEqual(len(self._support_emails()), 1)


class AssessmentRequestCancelTests(TestCase):
    def setUp(self):
        self.student = _subscriber('student@example.com', 'Sue')
        self.other = _subscriber('other@example.com', 'Omar')
        self.assessment_request = AssessmentRequest.objects.create(
            student=self.student, level='level2', test_type='speaking')

    def test_owner_can_cancel_pending_request(self):
        self.client.force_login(self.student)
        response = self.client.post(
            reverse('cancel_assessment_request', args=[self.assessment_request.id]))
        self.assertRedirects(response, reverse('test_list'))
        self.assessment_request.refresh_from_db()
        self.assertEqual(self.assessment_request.status, 'cancelled')

    def test_non_owner_cannot_cancel(self):
        self.client.force_login(self.other)
        response = self.client.post(
            reverse('cancel_assessment_request', args=[self.assessment_request.id]))
        self.assertEqual(response.status_code, 404)
        self.assessment_request.refresh_from_db()
        self.assertEqual(self.assessment_request.status, 'pending')


class AllTestsTimedTests(TestCase):
    """Cece (2026-11-03): all tests should be timed. Tests without an
    instructor-set limit fall back to the 30-minute default."""

    def setUp(self):
        self.student = _subscriber('timed@example.com', 'Tia')

    def _plain_test(self, **kwargs):
        defaults = dict(
            title='Plain Test', level='Level I', test_type='listening',
            is_active=True, is_published=True)
        defaults.update(kwargs)
        return LanguageTest.objects.create(**defaults)

    def _deadline_minutes(self, test):
        self.client.force_login(self.student)
        self.client.get(reverse('take_test', args=[test.id]))
        attempt = TimedTestAttempt.objects.get(student=self.student, test=test)
        return (attempt.deadline - timezone.now()).total_seconds() / 60

    def test_test_without_limit_uses_default_deadline(self):
        test = self._plain_test(time_limit_minutes=None)
        minutes = self._deadline_minutes(test)
        self.assertAlmostEqual(minutes, DEFAULT_TEST_TIME_LIMIT_MINUTES, delta=1)

    def test_instructor_set_limit_is_respected(self):
        test = self._plain_test(time_limit_minutes=45)
        minutes = self._deadline_minutes(test)
        self.assertAlmostEqual(minutes, 45, delta=1)

    def test_generated_listening_assessment_is_timed(self):
        for i in range(12):
            _vocabulary(f'timed-word-{i}', f'timed translation {i}')
        self.client.force_login(self.student)
        self.client.post(reverse('request_assessment'),
                         {'level': 'level1', 'test_type': 'listening'})
        test = LanguageTest.objects.get(assigned_students=self.student)
        self.assertEqual(test.time_limit_minutes, DEFAULT_TEST_TIME_LIMIT_MINUTES)
