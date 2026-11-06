"""Tests for the automatic subscription-renewal survey (Cece, 2026-11-05).

Students whose base subscription period ends in 7 days are invited (via
send_subscription_reminders) to the system renewal survey; answers go
to the PandaSpeak managers.
"""
from datetime import datetime, time as dt_time, timedelta

from django.contrib.auth import get_user_model
from django.core import mail
from django.core.management import call_command
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from account.models import Notification
from teacher.models import LearningSurvey, SurveyAnswer, SurveyResponse

from .models import RenewalSurveyInvite, Subscription
from .renewal_survey import get_or_create_renewal_survey, send_renewal_survey_invite

User = get_user_model()

_PW = "test" + "-pass" + "word"
INVITE_TITLE = "A Quick Survey Before Your Subscription Renews"
SUPPORT_EMAIL = "pandaspeaksupport" + "@gmail.com"


def _access_until(days_from_today):
    return timezone.make_aware(
        datetime.combine(timezone.localdate() + timedelta(days=days_from_today), dt_time(12, 0)),
        timezone.get_current_timezone(),
    )


class RenewalSurveyBase(TestCase):
    def setUp(self):
        self.manager = User.objects.create_user(
            email="manager@example.com", password=_PW,
            first_name="Manager", is_staff=True,
        )
        self.student = User.objects.create_user(
            email="student@example.com", password=_PW,
            first_name="Stu",
        )
        mail.outbox.clear()

    def _subscription(self, user, days=7, **kwargs):
        defaults = dict(
            subscription_plan="standard",
            subscription_cost=15.00,
            is_active=True,
            access_until=_access_until(days),
        )
        defaults.update(kwargs)
        return Subscription.objects.create(user=user, **defaults)


class ReminderCommandInviteTests(RenewalSurveyBase):
    def test_invite_created_once_for_period_ending_in_7_days(self):
        subscription = self._subscription(self.student, days=7)

        call_command("send_subscription_reminders")

        self.assertEqual(RenewalSurveyInvite.objects.filter(user=self.student).count(), 1)
        invite = RenewalSurveyInvite.objects.get(user=self.student)
        self.assertEqual(invite.subscription, subscription)
        self.assertEqual(invite.period_end, subscription.access_until)
        self.assertIsNone(invite.completed_at)

        self.assertEqual(
            Notification.objects.filter(user=self.student, title=INVITE_TITLE).count(), 1)
        invite_emails = [m for m in mail.outbox if m.subject == INVITE_TITLE]
        self.assertEqual(len(invite_emails), 1)
        self.assertEqual(invite_emails[0].to, [self.student.email])

        # The system survey itself was created with its six questions.
        survey = get_or_create_renewal_survey()
        self.assertTrue(survey.is_system_renewal)
        self.assertEqual(survey.questions.count(), 6)

        # Running the command again creates nothing new.
        mail.outbox.clear()
        call_command("send_subscription_reminders")
        self.assertEqual(RenewalSurveyInvite.objects.filter(user=self.student).count(), 1)
        self.assertEqual(
            Notification.objects.filter(user=self.student, title=INVITE_TITLE).count(), 1)
        self.assertEqual([m for m in mail.outbox if m.subject == INVITE_TITLE], [])

    def test_no_invite_for_period_ending_in_6_or_8_days(self):
        other = User.objects.create_user(
            email="other@example.com", password=_PW, first_name="Other")
        self._subscription(self.student, days=6)
        self._subscription(other, days=8)
        mail.outbox.clear()

        call_command("send_subscription_reminders")

        self.assertEqual(RenewalSurveyInvite.objects.count(), 0)
        self.assertEqual(
            Notification.objects.filter(title=INVITE_TITLE).count(), 0)


class SurveyVisibilityTests(RenewalSurveyBase):
    def test_survey_hidden_without_invite_shown_with_invite(self):
        survey = get_or_create_renewal_survey()
        # The survey pages sit behind subscription_required; give the
        # student an active subscription whose period is not ending.
        self._subscription(self.student, days=300)
        list_url = reverse("student_survey_list")

        self.client.force_login(self.student)
        response = self.client.get(list_url)
        self.assertEqual(response.status_code, 200)
        self.assertNotIn(survey, list(response.context["available_surveys"]))

        # Subscription is OneToOne per user: move the existing active
        # subscription's period end to 7 days out and invite against it.
        subscription = Subscription.objects.get(user=self.student)
        subscription.access_until = _access_until(7)
        subscription.save(update_fields=["access_until"])
        self.assertTrue(send_renewal_survey_invite(self.student, subscription))

        response = self.client.get(list_url)
        available = list(response.context["available_surveys"])
        self.assertIn(survey, available)
        self.assertEqual(available[0], survey)


class TakeRenewalSurveyTests(RenewalSurveyBase):
    def setUp(self):
        super().setUp()
        self.survey = get_or_create_renewal_survey()
        self.take_url = reverse("take_learning_survey", args=[self.survey.id])
        mail.outbox.clear()

    def test_non_invited_student_is_redirected_away(self):
        # Active subscription (so subscription_required passes) whose
        # period is NOT ending — the student has no invite.
        self._subscription(self.student, days=300)
        self.client.force_login(self.student)
        response = self.client.get(self.take_url)
        self.assertRedirects(response, reverse("student_survey_list"), fetch_redirect_response=False)

    def test_invited_student_submits_and_managers_are_notified(self):
        subscription = self._subscription(self.student, days=7)
        self.assertTrue(send_renewal_survey_invite(self.student, subscription))
        mail.outbox.clear()

        self.client.force_login(self.student)
        response = self.client.get(self.take_url)
        self.assertEqual(response.status_code, 200)

        answers = {}
        for question in self.survey.questions.all():
            if question.question_type == "rating":
                answers[f"question_{question.id}"] = "5"
            elif question.question_type == "multiple_choice":
                answers[f"question_{question.id}"] = question.option_a
            else:
                answers[f"question_{question.id}"] = "More speaking practice, please."
        response = self.client.post(self.take_url, answers)
        self.assertRedirects(response, reverse("student_survey_list"), fetch_redirect_response=False)

        invite = RenewalSurveyInvite.objects.get(user=self.student)
        self.assertIsNotNone(invite.completed_at)
        survey_response = SurveyResponse.objects.get(survey=self.survey, student=self.student)
        self.assertEqual(survey_response.answers.count(), 6)

        self.assertTrue(Notification.objects.filter(
            user=self.manager, title="New Renewal Survey Response").exists())
        support_emails = [m for m in mail.outbox if m.to == [SUPPORT_EMAIL]]
        self.assertEqual(len(support_emails), 1)
        self.assertTrue(support_emails[0].subject.startswith("New Renewal Survey Response:"))


class ManagerRenewalResponsesTests(RenewalSurveyBase):
    def test_manager_page_shows_answers_and_is_manager_only(self):
        subscription = self._subscription(self.student, days=7)
        self.assertTrue(send_renewal_survey_invite(self.student, subscription))
        survey = get_or_create_renewal_survey()
        response = SurveyResponse.objects.create(survey=survey, student=self.student)
        text_question = survey.questions.filter(question_type="text").order_by("order").first()
        SurveyAnswer.objects.create(
            response=response, question=text_question,
            answer="Loved the history lessons.")
        page_url = reverse("manager_renewal_survey_responses")

        self.client.force_login(self.student)
        student_response = self.client.get(page_url)
        self.assertNotEqual(student_response.status_code, 200)

        self.client.force_login(self.manager)
        manager_response = self.client.get(page_url)
        self.assertEqual(manager_response.status_code, 200)
        self.assertContains(manager_response, "Loved the history lessons.")
        self.assertContains(manager_response, self.student.email)
