"""Tests for manager-created assessment tests and manager speaking grading.

Covers Cece's 2026-11-03 specs:
- A manager can create a test for one student (e.g. to fulfil an
  AssessmentRequest) or for all users; manager tests live on the manager
  dashboard's Assessment Tests page, where the audience can be edited to
  add more users and tests can be deleted.
- When a student completes a manager speaking test, the managers are
  notified (support email + staff Notification) and a manager scores the
  speaking part on the manager grading pages.
- Auto-generated assessment tests (Cece's revised 2026-11-03 flow) are
  manager-scored through their fulfilled AssessmentRequest link: their
  submissions notify managers and appear on the grading pages, but the
  tests themselves never appear on the manager test list.
"""
import tempfile
from datetime import timedelta
from decimal import Decimal

from django.core import mail
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import timezone

from student.models import (AssessmentRequest, LanguageTest,
                            StudentSpeakingAnswer, StudentTestSubmission,
                            TestQuestion, TimedTestAttempt)
from student.timed_tests import (finalize_attempt,
                                 notify_managers_speaking_submission)
from subscription.models import Subscription

from .models import CustomUser, Notification


def _subscriber(email, first_name='Pat'):
    user = CustomUser.objects.create_user(
        email=email, password='<redacted>', first_name=first_name, last_name='Student')
    Subscription.objects.create(
        user=user, subscription_plan='Base', subscription_cost=Decimal('15.00'), is_active=True)
    return user


def _manager(email='manager@example.com'):
    return CustomUser.objects.create_user(
        email, 'test', is_staff=True, first_name='Mary', last_name='Manager')


def _support_emails():
    return [m for m in mail.outbox if m.to == ['pandaspeaksupport@gmail.com']]


def _manager_test(**kwargs):
    defaults = dict(
        title='Manager Speaking Test', level='Level II', test_type='speaking',
        is_active=True, is_published=True, is_manager_test=True)
    defaults.update(kwargs)
    return LanguageTest.objects.create(**defaults)


def _speak_question(test, prompt='Read this aloud.', points=5, order=1):
    return TestQuestion.objects.create(
        test=test, question_type='speak_read', prompt=prompt,
        points=points, order=order)


class ManagerAccessTests(TestCase):
    def setUp(self):
        self.manager = _manager()
        self.student = _subscriber('student@example.com', 'Sue')

    def test_non_manager_redirected_from_test_list(self):
        self.client.force_login(self.student)
        response = self.client.get(reverse('manager_test_list'))
        self.assertRedirects(response, reverse('home'))

    def test_non_manager_blocked_from_grading_pages(self):
        test = _manager_test()
        submission = StudentTestSubmission.objects.create(
            student=self.student, test=test, listening_score=0)
        self.client.force_login(self.student)
        for url in (
            reverse('manager_grading_list'),
            reverse('manager_grading_detail', args=[submission.id]),
            reverse('manager_create_test'),
        ):
            response = self.client.get(url)
            self.assertRedirects(response, reverse('home'))

    def test_manager_can_open_test_list(self):
        self.client.force_login(self.manager)
        response = self.client.get(reverse('manager_test_list'))
        self.assertEqual(response.status_code, 200)


class ManagerPageRenderTests(TestCase):
    def setUp(self):
        self.manager = _manager()
        self.test = _manager_test()
        _speak_question(self.test)
        self.client.force_login(self.manager)

    def test_manager_pages_render(self):
        for url in (
            reverse('manager_test_list'),
            reverse('manager_create_test'),
            reverse('manager_edit_test', args=[self.test.id]),
            reverse('manager_test_questions', args=[self.test.id]),
            reverse('manager_delete_test', args=[self.test.id]),
            reverse('manager_grading_list'),
        ):
            response = self.client.get(url)
            self.assertEqual(response.status_code, 200, url)


class ManagerCreateFromRequestTests(TestCase):
    def setUp(self):
        self.manager = _manager()
        self.student = _subscriber('requester@example.com', 'Rita')
        self.other = _subscriber('other@example.com', 'Omar')
        self.assessment_request = AssessmentRequest.objects.create(
            student=self.student, level='level2', test_type='speaking')

    def test_create_from_request_prefills_form(self):
        self.client.force_login(self.manager)
        response = self.client.get(
            reverse('manager_create_test'),
            {'request': self.assessment_request.id})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['assessment_request'], self.assessment_request)
        initial = response.context['form'].initial
        self.assertEqual(initial['audience'], str(self.student.id))
        self.assertEqual(initial['level'], 'Level II')
        self.assertEqual(initial['test_type'], 'speaking')
        self.assertEqual(initial['title'], 'Level II Speaking Assessment')

    def test_create_add_question_and_publish_fulfils_request(self):
        self.client.force_login(self.manager)
        response = self.client.post(reverse('manager_create_test'), {
            'title': 'Level II Speaking Assessment',
            'level': 'Level II',
            'test_type': 'speaking',
            'description': '',
            'time_limit_minutes': '30',
            'available_from': '',
            'available_until': '',
            'is_active': 'on',
            'audience': str(self.student.id),
            'request_id': str(self.assessment_request.id),
        })
        test = LanguageTest.objects.get(is_manager_test=True)
        self.assertRedirects(
            response, reverse('manager_test_questions', args=[test.id]))
        self.assertIsNone(test.teacher)
        self.assertFalse(test.is_published)
        self.assertEqual(list(test.assigned_students.all()), [self.student])
        self.assessment_request.refresh_from_db()
        self.assertEqual(self.assessment_request.fulfilled_test, test)
        self.assertEqual(self.assessment_request.status, 'pending')

        response = self.client.post(
            reverse('manager_test_questions', args=[test.id]), {
                'question_type': 'speak_read',
                'prompt': 'Read this sentence aloud.',
                'choice_a': '', 'choice_b': '', 'choice_c': '', 'choice_d': '',
                'correct_answer': '', 'correct_choice': '',
                'points': '5', 'order': '1',
            })
        self.assertRedirects(
            response, reverse('manager_test_questions', args=[test.id]))
        self.assertEqual(test.questions.count(), 1)

        response = self.client.post(reverse('manager_publish_test', args=[test.id]))
        self.assertRedirects(response, reverse('manager_test_list'))
        test.refresh_from_db()
        self.assertTrue(test.is_published)
        self.assessment_request.refresh_from_db()
        self.assertEqual(self.assessment_request.status, 'fulfilled')
        publish_emails = [
            m for m in mail.outbox
            if m.to == [self.student.email]
            and m.subject == f'New PandaSpeak Test: {test.title}']
        self.assertEqual(len(publish_emails), 1)

        self.client.force_login(self.student)
        response = self.client.get(reverse('test_list'))
        self.assertIn(test, list(response.context['tests']))

        self.client.force_login(self.other)
        response = self.client.get(reverse('test_list'))
        self.assertNotIn(test, list(response.context['tests']))


class ManagerAllUsersTests(TestCase):
    def setUp(self):
        self.manager = _manager()
        self.student = _subscriber('one@example.com', 'One')
        self.other = _subscriber('two@example.com', 'Two')

    def test_all_users_test_visible_to_every_student_after_publish(self):
        self.client.force_login(self.manager)
        self.client.post(reverse('manager_create_test'), {
            'title': 'Open Assessment',
            'level': 'Level I',
            'test_type': 'mixed',
            'description': '',
            'time_limit_minutes': '30',
            'available_from': '',
            'available_until': '',
            'is_active': 'on',
            'audience': '',
        })
        test = LanguageTest.objects.get(is_manager_test=True)
        self.assertEqual(test.assigned_students.count(), 0)

        self.client.post(reverse('manager_test_questions', args=[test.id]), {
            'question_type': 'speak_read',
            'prompt': 'Read this sentence aloud.',
            'choice_a': '', 'choice_b': '', 'choice_c': '', 'choice_d': '',
            'correct_answer': '', 'correct_choice': '',
            'points': '5', 'order': '1',
        })
        self.client.post(reverse('manager_publish_test', args=[test.id]))

        for user in (self.student, self.other):
            self.client.force_login(user)
            response = self.client.get(reverse('test_list'))
            self.assertIn(test, list(response.context['tests']))


class ManagerEditAudienceTests(TestCase):
    def setUp(self):
        self.manager = _manager()
        self.first = _subscriber('first@example.com', 'First')
        self.second = _subscriber('second@example.com', 'Second')
        self.third = _subscriber('third@example.com', 'Third')
        self.test = _manager_test(title='Editable Assessment')
        self.test.assigned_students.set([self.first])

    def _visible_to(self, user):
        self.client.force_login(user)
        response = self.client.get(reverse('test_list'))
        return self.test in list(response.context['tests'])

    def test_edit_adds_a_second_student(self):
        self.assertTrue(self._visible_to(self.first))
        self.assertFalse(self._visible_to(self.second))

        self.client.force_login(self.manager)
        response = self.client.post(
            reverse('manager_edit_test', args=[self.test.id]), {
                'title': 'Editable Assessment',
                'level': 'Level II',
                'test_type': 'speaking',
                'description': '',
                'time_limit_minutes': '30',
                'available_from': '',
                'available_until': '',
                'is_active': 'on',
                'students': [str(self.first.id), str(self.second.id)],
            })
        self.assertRedirects(response, reverse('manager_test_list'))
        self.assertEqual(
            set(self.test.assigned_students.all()), {self.first, self.second})

        self.assertTrue(self._visible_to(self.first))
        self.assertTrue(self._visible_to(self.second))
        self.assertFalse(self._visible_to(self.third))

    def test_edit_switch_back_to_all_users(self):
        self.client.force_login(self.manager)
        self.client.post(reverse('manager_edit_test', args=[self.test.id]), {
            'title': 'Editable Assessment',
            'level': 'Level II',
            'test_type': 'speaking',
            'description': '',
            'time_limit_minutes': '30',
            'available_from': '',
            'available_until': '',
            'is_active': 'on',
            'audience_all': 'on',
            'students': [str(self.first.id)],
        })
        self.assertEqual(self.test.assigned_students.count(), 0)
        self.assertTrue(self._visible_to(self.third))


class ManagerDeleteTests(TestCase):
    def setUp(self):
        self.manager = _manager()
        self.test = _manager_test()

    def test_manager_deletes_own_test_via_confirm_page(self):
        self.client.force_login(self.manager)
        response = self.client.get(reverse('manager_delete_test', args=[self.test.id]))
        self.assertEqual(response.status_code, 200)
        response = self.client.post(reverse('manager_delete_test', args=[self.test.id]))
        self.assertRedirects(response, reverse('manager_test_list'))
        self.assertFalse(LanguageTest.objects.filter(id=self.test.id).exists())

    def test_teacher_owned_test_cannot_be_managed(self):
        teacher = CustomUser.objects.create_user(
            'teacher@example.com', 'test', is_teacher=True)
        teacher_test = LanguageTest.objects.create(
            title='Teacher Test', level='Level I', test_type='speaking',
            teacher=teacher, is_manager_test=False)
        self.client.force_login(self.manager)
        response = self.client.post(
            reverse('manager_delete_test', args=[teacher_test.id]))
        self.assertEqual(response.status_code, 404)
        response = self.client.get(
            reverse('manager_edit_test', args=[teacher_test.id]))
        self.assertEqual(response.status_code, 404)
        response = self.client.get(
            reverse('manager_test_questions', args=[teacher_test.id]))
        self.assertEqual(response.status_code, 404)
        self.assertTrue(LanguageTest.objects.filter(id=teacher_test.id).exists())


class SpeakingCompletionNotificationTests(TestCase):
    def setUp(self):
        self.manager = _manager()
        self.student = _subscriber('speaker@example.com', 'Sue')
        self.test = _manager_test()
        self.question = _speak_question(self.test)

    def _attempt_with_recording(self):
        StudentSpeakingAnswer.objects.create(
            student=self.student, question=self.question,
            audio_file='speaking_answers/recording.webm')
        return TimedTestAttempt.objects.create(
            student=self.student, test=self.test,
            deadline=timezone.now() + timedelta(minutes=30))

    def test_finalize_attempt_notifies_managers_exactly_once(self):
        attempt = self._attempt_with_recording()
        submission = finalize_attempt(attempt.id)
        self.assertIsNotNone(submission)
        answer = StudentSpeakingAnswer.objects.get(student=self.student)
        self.assertEqual(answer.submission, submission)

        support = _support_emails()
        self.assertEqual(len(support), 1)
        self.assertEqual(support[0].subject, 'Speaking test completed — ready to score')
        self.assertIn(self.student.email, support[0].body)
        self.assertIn(self.test.title, support[0].body)
        self.assertIn(
            reverse('manager_grading_detail', args=[submission.id]),
            support[0].body)
        notifications = Notification.objects.filter(
            user=self.manager, title='Speaking Test Ready to Score')
        self.assertEqual(notifications.count(), 1)
        self.assertEqual(
            notifications.get().link,
            reverse('manager_grading_detail', args=[submission.id]))

        # Idempotent: finalizing again returns the same submission and
        # sends no further alerts.
        again = finalize_attempt(attempt.id)
        self.assertEqual(again, submission)
        self.assertEqual(len(_support_emails()), 1)
        self.assertEqual(
            Notification.objects.filter(
                user=self.manager, title='Speaking Test Ready to Score').count(),
            1)

    def test_notify_helper_ignores_teacher_tests(self):
        teacher = CustomUser.objects.create_user(
            'teacher@example.com', 'test', is_teacher=True)
        teacher_test = LanguageTest.objects.create(
            title='Teacher Speaking Test', level='Level I',
            test_type='speaking', teacher=teacher, is_manager_test=False)
        question = _speak_question(teacher_test)
        submission = StudentTestSubmission.objects.create(
            student=self.student, test=teacher_test, listening_score=0)
        StudentSpeakingAnswer.objects.create(
            student=self.student, question=question, submission=submission,
            audio_file='speaking_answers/recording.webm')
        notify_managers_speaking_submission(submission)
        self.assertEqual(_support_emails(), [])
        self.assertEqual(
            Notification.objects.filter(
                user=self.manager, title='Speaking Test Ready to Score').count(),
            0)

    def test_notify_helper_ignores_manager_test_without_speaking(self):
        listening_test = _manager_test(
            title='Manager Listening Test', test_type='listening')
        submission = StudentTestSubmission.objects.create(
            student=self.student, test=listening_test, listening_score=10)
        notify_managers_speaking_submission(submission)
        self.assertEqual(_support_emails(), [])


@override_settings(MEDIA_ROOT=tempfile.mkdtemp())
class ManagerGradingTests(TestCase):
    def setUp(self):
        self.manager = _manager()
        self.student = _subscriber('graded@example.com', 'Gail')
        self.test = _manager_test()
        self.question1 = _speak_question(self.test, 'Read sentence one.', points=5, order=1)
        self.question2 = _speak_question(self.test, 'Read sentence two.', points=3, order=2)
        self.submission = StudentTestSubmission.objects.create(
            student=self.student, test=self.test, listening_score=0)
        self.answer1 = StudentSpeakingAnswer.objects.create(
            student=self.student, question=self.question1,
            submission=self.submission,
            audio_file=SimpleUploadedFile('one.webm', b'fake-audio-1'))
        self.answer2 = StudentSpeakingAnswer.objects.create(
            student=self.student, question=self.question2,
            submission=self.submission,
            audio_file=SimpleUploadedFile('two.webm', b'fake-audio-2'))

    def test_grading_list_and_detail_show_submission(self):
        self.client.force_login(self.manager)
        response = self.client.get(reverse('manager_grading_list'))
        self.assertEqual(response.status_code, 200)
        listed = {s.id: s for s in response.context['submissions']}
        self.assertIn(self.submission.id, listed)
        self.assertEqual(listed[self.submission.id].speaking_total, 2)
        self.assertEqual(listed[self.submission.id].speaking_graded, 0)

        response = self.client.get(
            reverse('manager_grading_detail', args=[self.submission.id]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            {a.id for a in response.context['speaking_answers']},
            {self.answer1.id, self.answer2.id})

    def test_grading_flow_scores_and_completes(self):
        self.client.force_login(self.manager)
        response = self.client.post(
            reverse('manager_grade_speaking_answer', args=[self.answer1.id]),
            {'score': '4', 'teacher_feedback': 'Good pronunciation.'})
        self.assertRedirects(
            response,
            reverse('manager_grading_detail', args=[self.submission.id]))
        self.answer1.refresh_from_db()
        self.assertEqual(self.answer1.score, 4.0)
        self.assertEqual(self.answer1.teacher_feedback, 'Good pronunciation.')
        self.assertFalse(self.answer1.audio_file)  # recording removed after grading
        self.submission.refresh_from_db()
        self.assertEqual(self.submission.speaking_score, 4.0)
        self.assertFalse(self.submission.is_graded)

        # Out-of-range scores are rejected with the teacher flow's message.
        response = self.client.post(
            reverse('manager_grade_speaking_answer', args=[self.answer2.id]),
            {'score': '99', 'teacher_feedback': ''},
            follow=True)
        self.assertContains(response, 'Score must be between 0 and 3.')
        self.answer2.refresh_from_db()
        self.assertIsNone(self.answer2.score)

        response = self.client.post(
            reverse('manager_grade_speaking_answer', args=[self.answer2.id]),
            {'score': '3', 'teacher_feedback': 'Well done.'})
        self.assertRedirects(
            response,
            reverse('manager_grading_detail', args=[self.submission.id]))
        self.submission.refresh_from_db()
        self.assertEqual(self.submission.speaking_score, 7.0)
        self.assertEqual(self.submission.total_score, 7.0)
        self.assertTrue(self.submission.is_graded)
        self.assertTrue(
            Notification.objects.filter(
                user=self.student, title='Test Graded').exists())

    def test_grading_answer_on_teacher_test_404s(self):
        teacher = CustomUser.objects.create_user(
            'teacher@example.com', 'test', is_teacher=True)
        teacher_test = LanguageTest.objects.create(
            title='Teacher Speaking Test', level='Level I',
            test_type='speaking', teacher=teacher, is_manager_test=False)
        question = _speak_question(teacher_test)
        submission = StudentTestSubmission.objects.create(
            student=self.student, test=teacher_test, listening_score=0)
        answer = StudentSpeakingAnswer.objects.create(
            student=self.student, question=question, submission=submission,
            audio_file='speaking_answers/recording.webm')
        self.client.force_login(self.manager)
        response = self.client.post(
            reverse('manager_grade_speaking_answer', args=[answer.id]),
            {'score': '1', 'teacher_feedback': ''})
        self.assertEqual(response.status_code, 404)
        answer.refresh_from_db()
        self.assertIsNone(answer.score)


def _generated_assessment_test(student, **kwargs):
    """An auto-generated assessment test: NOT manager-created, so it is
    manager-scored only through the fulfilled AssessmentRequest that was
    recorded with it (see student.assessment)."""
    defaults = dict(
        title='Level II Speaking Assessment', level='Level II',
        test_type='speaking', is_active=True, is_published=True,
        is_manager_test=False)
    defaults.update(kwargs)
    test = LanguageTest.objects.create(**defaults)
    test.assigned_students.set([student])
    AssessmentRequest.objects.create(
        student=student, level='level2', test_type='speaking',
        status='fulfilled', fulfilled_test=test)
    return test


class GeneratedAssessmentNotificationTests(TestCase):
    """A submission on an auto-generated assessment test alerts the
    managers exactly like a manager-created test does."""

    def setUp(self):
        self.manager = _manager()
        self.student = _subscriber('gen-speaker@example.com', 'Gwen')
        self.test = _generated_assessment_test(self.student)
        self.question = _speak_question(self.test)

    def test_finalize_attempt_notifies_managers_for_generated_test(self):
        StudentSpeakingAnswer.objects.create(
            student=self.student, question=self.question,
            audio_file='speaking_answers/recording.webm')
        attempt = TimedTestAttempt.objects.create(
            student=self.student, test=self.test,
            deadline=timezone.now() + timedelta(minutes=30))

        submission = finalize_attempt(attempt.id)
        self.assertIsNotNone(submission)
        support = _support_emails()
        self.assertEqual(len(support), 1)
        self.assertEqual(support[0].subject, 'Speaking test completed — ready to score')
        self.assertIn(self.student.email, support[0].body)
        self.assertIn(self.test.title, support[0].body)
        self.assertIn(
            reverse('manager_grading_detail', args=[submission.id]),
            support[0].body)
        notifications = Notification.objects.filter(
            user=self.manager, title='Speaking Test Ready to Score')
        self.assertEqual(notifications.count(), 1)

        # Idempotent: finalizing again sends no further alerts.
        again = finalize_attempt(attempt.id)
        self.assertEqual(again, submission)
        self.assertEqual(len(_support_emails()), 1)
        self.assertEqual(
            Notification.objects.filter(
                user=self.manager, title='Speaking Test Ready to Score').count(),
            1)


@override_settings(MEDIA_ROOT=tempfile.mkdtemp())
class GeneratedAssessmentGradingTests(TestCase):
    """Submissions on auto-generated assessment tests appear on the
    manager grading pages even though the tests are not manager-created,
    and grading them works end to end."""

    def setUp(self):
        self.manager = _manager()
        self.student = _subscriber('gen-graded@example.com', 'Gail')
        self.test = _generated_assessment_test(self.student)
        self.question1 = _speak_question(self.test, 'Read sentence one.', points=5, order=1)
        self.question2 = _speak_question(self.test, 'Read sentence two.', points=3, order=2)
        self.submission = StudentTestSubmission.objects.create(
            student=self.student, test=self.test, listening_score=0)
        self.answer1 = StudentSpeakingAnswer.objects.create(
            student=self.student, question=self.question1,
            submission=self.submission,
            audio_file=SimpleUploadedFile('one.webm', b'fake-audio-1'))
        self.answer2 = StudentSpeakingAnswer.objects.create(
            student=self.student, question=self.question2,
            submission=self.submission,
            audio_file=SimpleUploadedFile('two.webm', b'fake-audio-2'))

    def test_grading_list_and_detail_include_generated_submission(self):
        self.client.force_login(self.manager)
        response = self.client.get(reverse('manager_grading_list'))
        self.assertEqual(response.status_code, 200)
        listed = {s.id: s for s in response.context['submissions']}
        self.assertIn(self.submission.id, listed)
        self.assertEqual(listed[self.submission.id].speaking_total, 2)
        self.assertEqual(listed[self.submission.id].speaking_graded, 0)

        response = self.client.get(
            reverse('manager_grading_detail', args=[self.submission.id]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            {a.id for a in response.context['speaking_answers']},
            {self.answer1.id, self.answer2.id})

    def test_grading_generated_submission_flips_is_graded(self):
        self.client.force_login(self.manager)
        self.client.post(
            reverse('manager_grade_speaking_answer', args=[self.answer1.id]),
            {'score': '5', 'teacher_feedback': 'Perfect.'})
        self.submission.refresh_from_db()
        self.assertEqual(self.submission.speaking_score, 5.0)
        self.assertFalse(self.submission.is_graded)

        self.client.post(
            reverse('manager_grade_speaking_answer', args=[self.answer2.id]),
            {'score': '2', 'teacher_feedback': 'Keep practicing.'})
        self.submission.refresh_from_db()
        self.assertEqual(self.submission.speaking_score, 7.0)
        self.assertEqual(self.submission.total_score, 7.0)
        self.assertTrue(self.submission.is_graded)
        self.assertTrue(
            Notification.objects.filter(
                user=self.student, title='Test Graded').exists())

    def test_generated_test_not_in_manager_test_list(self):
        # Generated tests surface only through grading, never as
        # editable manager tests.
        self.client.force_login(self.manager)
        response = self.client.get(reverse('manager_test_list'))
        self.assertEqual(response.status_code, 200)
        self.assertNotIn(self.test, list(response.context['tests']))
        response = self.client.get(
            reverse('manager_edit_test', args=[self.test.id]))
        self.assertEqual(response.status_code, 404)

    def test_grading_detail_404_for_plain_teacher_test(self):
        teacher = CustomUser.objects.create_user(
            'teacher@example.com', 'test', is_teacher=True)
        teacher_test = LanguageTest.objects.create(
            title='Teacher Speaking Test', level='Level I',
            test_type='speaking', teacher=teacher, is_manager_test=False)
        question = _speak_question(teacher_test)
        submission = StudentTestSubmission.objects.create(
            student=self.student, test=teacher_test, listening_score=0)
        StudentSpeakingAnswer.objects.create(
            student=self.student, question=question, submission=submission,
            audio_file='speaking_answers/recording.webm')
        self.client.force_login(self.manager)
        response = self.client.get(
            reverse('manager_grading_detail', args=[submission.id]))
        self.assertEqual(response.status_code, 404)
        response = self.client.get(reverse('manager_grading_list'))
        listed_ids = {s.id for s in response.context['submissions']}
        self.assertNotIn(submission.id, listed_ids)
