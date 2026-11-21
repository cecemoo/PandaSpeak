"""Tests for the Terms/FAQ checkbox gate on tutoring checkout.

Mirrors the subscription checkout consent: both the Terms of Service and
FAQ acknowledgements must be submitted before a tutoring Stripe checkout
starts, and the acceptance is recorded as a SubscriptionConsentEvent with
provider "tutoring" so it appears on the manager Acknowledgements page.
"""
from datetime import timedelta
from unittest import mock

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from account.models import CustomUser
from course.models import Course, TimeSlot
from subscription.models import SubscriptionConsentEvent, TutoringPayment

BOTH = {'accept_subscription_terms': 'yes', 'accept_subscription_faq': 'yes'}


class CartCheckoutConsentTests(TestCase):
    def setUp(self):
        self.student = CustomUser.objects.create_user(
            email='student@example.com', password='<redacted>',
            first_name='Stu', last_name='Dent')
        teacher = CustomUser.objects.create_user(
            email='tutor@example.com', password='<redacted>',
            first_name='Tess', last_name='Teacher', is_teacher=True)
        course = Course.objects.create(
            teacher=teacher, title='Conversation course', description='d',
            price=2000, duration_minutes=60, session_type='private',
            max_students=1)
        now = timezone.now()
        self.slot = TimeSlot.objects.create(
            course=course, start_time=now + timedelta(days=1),
            end_time=now + timedelta(days=1, hours=1), capacity=1)
        self.client.force_login(self.student)
        session = self.client.session
        session['cart'] = [self.slot.pk]
        session.save()

    def _post(self, data=None):
        with mock.patch('course.views.stripe.checkout.Session.create') as create:
            create.return_value = mock.Mock(
                url='https://checkout.stripe.com/test-session')
            response = self.client.post(reverse('course:cart_checkout'), data or {})
            return response, create

    def test_checkout_without_consent_is_refused(self):
        response, create = self._post()
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse('course:view_cart'), response.url)
        create.assert_not_called()
        self.assertEqual(SubscriptionConsentEvent.objects.count(), 0)

    def test_checkout_with_only_terms_is_refused(self):
        response, create = self._post({'accept_subscription_terms': 'yes'})
        self.assertEqual(response.status_code, 302)
        create.assert_not_called()
        self.assertEqual(SubscriptionConsentEvent.objects.count(), 0)

    def test_checkout_with_only_faq_is_refused(self):
        response, create = self._post({'accept_subscription_faq': 'yes'})
        self.assertEqual(response.status_code, 302)
        create.assert_not_called()
        self.assertEqual(SubscriptionConsentEvent.objects.count(), 0)

    def test_checkout_with_both_proceeds_and_records_consent(self):
        response, create = self._post(BOTH)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, 'https://checkout.stripe.com/test-session')
        create.assert_called_once()
        event = SubscriptionConsentEvent.objects.get()
        self.assertEqual(event.user, self.student)
        self.assertEqual(event.payment_provider, 'tutoring')
        self.assertTrue(event.terms_accepted)
        self.assertTrue(event.faq_accepted)


class LegacyTutoringCheckoutConsentTests(TestCase):
    def setUp(self):
        self.student = CustomUser.objects.create_user(
            email='legacy@example.com', password='<redacted>',
            first_name='Leg', last_name='Acey')
        self.payment = TutoringPayment.objects.create(
            student_name=self.student, class_name='Conversation',
            amount='25.00')
        self.client.force_login(self.student)
        self.url = reverse(
            'create_tutoring_checkout_session', args=[self.payment.pk])

    def test_get_without_consent_is_refused(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse('course:view_cart'), response.url)
        self.assertEqual(SubscriptionConsentEvent.objects.count(), 0)

    def test_post_with_only_terms_is_refused(self):
        response = self.client.post(self.url, {'accept_subscription_terms': 'yes'})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(SubscriptionConsentEvent.objects.count(), 0)


class TutoringConsentManagerRecordTests(TestCase):
    def test_tutoring_consent_appears_on_acknowledgements_page(self):
        student = CustomUser.objects.create_user(
            email='rec@example.com', password='<redacted>',
            first_name='Rec', last_name='Ord')
        SubscriptionConsentEvent.objects.create(
            user=student, terms_version='2026-10-10', terms_accepted=True,
            faq_accepted=True, payment_provider='tutoring')
        manager = CustomUser.objects.create_user(
            email='mgr@example.com', password='<redacted>',
            first_name='Man', last_name='Ager', is_staff=True,
            is_superuser=True)
        self.client.force_login(manager)
        response = self.client.get(reverse('manager_acknowledgement_records'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'tutoring')
        self.assertContains(response, 'rec@example.com')
