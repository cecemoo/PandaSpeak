"""Tests for comprehensive assessment requests from the Test List page.

Covers Cece's 2026-11-03 spec: listening-only requests are generated
instantly from the chosen level's materials and assigned to the requesting
student only; speaking / speaking & listening requests are recorded as
pending AssessmentRequests for the PandaSpeak team (with an email alert)
and can be cancelled by their owner.
"""
from decimal import Decimal

from django.core import mail
from django.test import TestCase
from django.urls import reverse

from account.models import CustomUser
from subscription.models import Subscription
from teacher.models import Vocabulary

from .models import AssessmentRequest, LanguageTest


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
        test = LanguageTest.objects.get(assigned_student=self.student)
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
        test = LanguageTest.objects.get(assigned_student=self.student)

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
        test = LanguageTest.objects.get(assigned_student=self.student)
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


class SpeakingAssessmentRequestTests(TestCase):
    def setUp(self):
        self.student = _subscriber('student@example.com', 'Sue')
        self.other = _subscriber('other@example.com', 'Omar')

    def _request(self, user, **overrides):
        data = {'level': 'level2', 'test_type': 'speaking'}
        data.update(overrides)
        self.client.force_login(user)
        return self.client.post(reverse('request_assessment'), data)

    def _support_emails(self):
        # Creating a Subscription also sends the user mail (subscription
        # signals), so count only the alerts addressed to the support inbox.
        return [m for m in mail.outbox if m.to == ['pandaspeaksupport@gmail.com']]

    def test_speaking_request_creates_pending_request_and_emails_support(self):
        response = self._request(self.student)
        self.assertRedirects(response, reverse('test_list'))
        assessment_request = AssessmentRequest.objects.get(student=self.student)
        self.assertEqual(assessment_request.level, 'level2')
        self.assertEqual(assessment_request.test_type, 'speaking')
        self.assertEqual(assessment_request.status, 'pending')
        support_emails = self._support_emails()
        self.assertEqual(len(support_emails), 1)
        message = support_emails[0]
        self.assertIn('Level II', message.subject)
        self.assertIn('Speaking', message.subject)
        self.assertIn(self.student.email, message.body)

    def test_mixed_request_is_recorded_as_mixed(self):
        self._request(self.student, test_type='mixed')
        assessment_request = AssessmentRequest.objects.get(student=self.student)
        self.assertEqual(assessment_request.test_type, 'mixed')
        self.assertEqual(assessment_request.status, 'pending')
        self.assertEqual(len(self._support_emails()), 1)

    def test_duplicate_pending_request_creates_no_second_record(self):
        self._request(self.student)
        self._request(self.student)
        self.assertEqual(AssessmentRequest.objects.count(), 1)
        self.assertEqual(len(self._support_emails()), 1)

    def test_owner_can_cancel_pending_request(self):
        self._request(self.student)
        assessment_request = AssessmentRequest.objects.get(student=self.student)
        self.client.force_login(self.student)
        response = self.client.post(
            reverse('cancel_assessment_request', args=[assessment_request.id]))
        self.assertRedirects(response, reverse('test_list'))
        assessment_request.refresh_from_db()
        self.assertEqual(assessment_request.status, 'cancelled')

    def test_non_owner_cannot_cancel(self):
        self._request(self.student)
        assessment_request = AssessmentRequest.objects.get(student=self.student)
        self.client.force_login(self.other)
        response = self.client.post(
            reverse('cancel_assessment_request', args=[assessment_request.id]))
        self.assertEqual(response.status_code, 404)
        assessment_request.refresh_from_db()
        self.assertEqual(assessment_request.status, 'pending')
