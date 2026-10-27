from datetime import datetime, time as dt_time, timedelta
from decimal import Decimal
from unittest.mock import Mock, patch

from django.contrib.auth import get_user_model
from django.core import mail
from django.core.management import call_command
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from account.models import Notification

from .models import Subscription, SubscriptionConsentEvent
from .plan_access import has_base_access
from .stripe_subscription_views import _update_subscription_dispute_status


User = get_user_model()


class StripeDisputeAccessTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="dispute-test@example.com",
            password="test-password",
            first_name="Dispute",
            last_name="Test",
        )
        self.subscription = Subscription.objects.create(
            user=self.user,
            subscription_plan="standard",
            subscription_cost=15.00,
            stripe_subscription_id="sub_test_123",
            is_active=True,
            plus_is_active=True,
            is_disputed=True,
            dispute_status="under_review",
            dispute_provider="stripe",
            dispute_external_id="dp_test_123",
            dispute_charge_id="ch_test_123",
        )

    def test_lost_stripe_dispute_keeps_all_paid_access_disabled(self):
        _update_subscription_dispute_status({"id": "dp_test_123", "status": "lost"})

        self.subscription.refresh_from_db()
        self.assertTrue(self.subscription.is_disputed)
        self.assertEqual(self.subscription.dispute_status, "lost")
        self.assertFalse(self.subscription.is_active)
        self.assertFalse(self.subscription.plus_is_active)

    def test_disputed_student_cannot_reach_any_student_route(self):
        self.client.force_login(self.user)

        response = self.client.get("/student/student_dashboard/")

        self.assertRedirects(
            response,
            reverse("dispute_restricted"),
            fetch_redirect_response=False,
        )

    def test_disputed_student_cannot_open_learning_materials(self):
        self.client.force_login(self.user)

        response = self.client.get("/student/access_learning_materials/")

        self.assertRedirects(
            response,
            reverse("dispute_restricted"),
            fetch_redirect_response=False,
        )


class PersistentStripeCheckoutTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="checkout-test@example.com", password="test-password"
        )
        self.client.force_login(self.user)

    @patch("subscription.stripe_subscription_views.stripe.checkout.Session.create")
    def test_first_checkout_persists_session(self, create):
        create.return_value = Mock(id="cs_test_first", url="https://checkout.stripe.com/test")
        response = self.client.post(reverse("stripe_subscription_checkout"), {"accept_subscription_terms": "yes", "accept_subscription_faq": "yes"})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "https://checkout.stripe.com/test")
        self.assertEqual(Subscription.objects.get(user=self.user).pending_stripe_checkout_id, "cs_test_first")

    @patch("subscription.stripe_subscription_views.stripe.checkout.Session.create")
    @patch("subscription.stripe_subscription_views.stripe.checkout.Session.retrieve")
    def test_retry_reuses_open_checkout(self, retrieve, create):
        Subscription.objects.create(
            user=self.user, subscription_plan="standard", subscription_cost=15,
            pending_stripe_checkout_id="cs_test_existing"
        )
        retrieve.return_value = Mock(status="open", url="https://checkout.stripe.com/existing")
        response = self.client.post(reverse("stripe_subscription_checkout"), {"accept_subscription_terms": "yes", "accept_subscription_faq": "yes"})
        self.assertEqual(response.url, "https://checkout.stripe.com/existing")
        create.assert_not_called()

    @patch("subscription.stripe_subscription_views.stripe.checkout.Session.create")
    @patch("subscription.stripe_subscription_views.stripe.checkout.Session.retrieve")
    def test_completed_checkout_never_creates_second_charge(self, retrieve, create):
        Subscription.objects.create(
            user=self.user, subscription_plan="standard", subscription_cost=15,
            pending_stripe_checkout_id="cs_test_completed"
        )
        retrieve.return_value = Mock(status="complete")
        response = self.client.post(reverse("stripe_subscription_checkout"), {"accept_subscription_terms": "yes", "accept_subscription_faq": "yes"})
        self.assertEqual(response.status_code, 302)
        create.assert_not_called()


class SubscriptionTermsAcknowledgementTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="terms-test@example.com", password="test-password"
        )
        self.client.force_login(self.user)

    def test_stripe_checkout_requires_terms_acknowledgement(self):
        from unittest.mock import patch
        with patch("subscription.stripe_subscription_views.stripe.checkout.Session.create") as create:
            response = self.client.post(reverse("stripe_subscription_checkout"))
            self.assertRedirects(response, reverse("subscribe"), fetch_redirect_response=False)
            create.assert_not_called()

    def test_paypal_checkout_requires_terms_acknowledgement(self):
        from unittest.mock import patch
        with patch("subscription.paypal_subscription_views._paypal_access_token") as token:
            response = self.client.post(reverse("subscribe"), {
                "payment_method": "paypal", "subscription_type": "yearly"
            })
            self.assertRedirects(response, reverse("subscribe"), fetch_redirect_response=False)
            token.assert_not_called()

    def test_acknowledgement_is_persisted_before_stripe_checkout(self):
        from unittest.mock import patch, Mock
        with patch("subscription.stripe_subscription_views.stripe.checkout.Session.create") as create:
            create.return_value = Mock(id="cs_terms", url="https://checkout.stripe.com/terms")
            response = self.client.post(reverse("stripe_subscription_checkout"), {
                "accept_subscription_terms": "yes", "accept_subscription_faq": "yes"
            })
        self.assertEqual(response.status_code, 302)
        subscription = Subscription.objects.get(user=self.user)
        self.assertIsNotNone(subscription.checkout_terms_accepted_at)
        self.assertEqual(subscription.checkout_terms_version, "2026-10-10")

    def test_terms_without_faq_does_not_record_consent(self):
        with patch("subscription.stripe_subscription_views.stripe.checkout.Session.create") as create:
            response = self.client.post(reverse("stripe_subscription_checkout"), {"accept_subscription_terms": "yes"})
        self.assertRedirects(response, reverse("subscribe"), fetch_redirect_response=False)
        create.assert_not_called()
        self.assertFalse(Subscription.objects.filter(user=self.user, checkout_terms_accepted_at__isnull=False).exists())

    def test_faq_without_terms_does_not_record_consent(self):
        with patch("subscription.stripe_subscription_views.stripe.checkout.Session.create") as create:
            response = self.client.post(reverse("stripe_subscription_checkout"), {"accept_subscription_faq": "yes"})
        self.assertRedirects(response, reverse("subscribe"), fetch_redirect_response=False)
        create.assert_not_called()
        self.assertFalse(Subscription.objects.filter(user=self.user, checkout_terms_accepted_at__isnull=False).exists())


class PlusUpgradeConsentTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="plus-terms-test@example.com", password="<redacted>"
        )
        Subscription.objects.create(
            user=self.user, subscription_plan="standard", subscription_cost=15,
            is_active=True,
        )
        self.client.force_login(self.user)

    def test_plus_checkout_requires_both_acknowledgements(self):
        from unittest.mock import patch
        with patch("subscription.stripe_subscription_views.stripe.checkout.Session.create") as create:
            response = self.client.post(reverse("stripe_plus_upgrade"))
            self.assertRedirects(response, reverse("plus_upgrade"), fetch_redirect_response=False)
            create.assert_not_called()
        self.assertFalse(SubscriptionConsentEvent.objects.filter(user=self.user).exists())

    def test_plus_checkout_terms_without_faq_does_not_record_consent(self):
        from unittest.mock import patch
        with patch("subscription.stripe_subscription_views.stripe.checkout.Session.create") as create:
            response = self.client.post(reverse("stripe_plus_upgrade"), {"accept_subscription_terms": "yes"})
            self.assertRedirects(response, reverse("plus_upgrade"), fetch_redirect_response=False)
            create.assert_not_called()
        self.assertFalse(SubscriptionConsentEvent.objects.filter(user=self.user).exists())

    def test_plus_checkout_with_both_acknowledgements_records_consent(self):
        from unittest.mock import patch, Mock
        with patch("subscription.stripe_subscription_views.stripe.checkout.Session.create") as create:
            create.return_value = Mock(id="cs_plus_terms", url="https://checkout.stripe.com/plus-terms")
            response = self.client.post(reverse("stripe_plus_upgrade"), {
                "accept_subscription_terms": "yes", "accept_subscription_faq": "yes"
            })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "https://checkout.stripe.com/plus-terms")
        self.assertEqual(SubscriptionConsentEvent.objects.filter(user=self.user).count(), 1)


class CheckoutConsentHistoryTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(email="history-test@example.com", password="password")
        self.client.force_login(self.user)

    @patch("subscription.stripe_subscription_views.stripe.checkout.Session.create")
    @patch("subscription.stripe_subscription_views.stripe.checkout.Session.retrieve")
    def test_repeat_checkout_retains_each_consent(self, retrieve, create):
        create.return_value = Mock(id="cs_history", url="https://checkout.stripe.com/history")
        retrieve.return_value = Mock(status="open", url="https://checkout.stripe.com/history")
        payload = {"accept_subscription_terms": "yes", "accept_subscription_faq": "yes"}
        self.client.post(reverse("stripe_subscription_checkout"), payload)
        self.client.post(reverse("stripe_subscription_checkout"), payload)
        self.assertEqual(SubscriptionConsentEvent.objects.filter(user=self.user).count(), 2)
        self.assertTrue(all(e.checkout_status == "initiated" for e in SubscriptionConsentEvent.objects.filter(user=self.user)))

    @patch("subscription.stripe_subscription_views.stripe.checkout.Session.create")
    def test_no_event_without_both_policies(self, create):
        self.client.post(reverse("stripe_subscription_checkout"), {"accept_subscription_terms": "yes"})
        self.assertFalse(SubscriptionConsentEvent.objects.filter(user=self.user).exists())
        create.assert_not_called()


class SchoolSubscriptionTests(TestCase):
    def setUp(self):
        self.manager = User.objects.create_user(
            email="manager@example.com", password="test-password", is_staff=True
        )
        self.student = User.objects.create_user(
            email="school-student@example.com",
            password="test-password",
            first_name="School",
            last_name="Student",
        )
        self.client.force_login(self.manager)
        self.end_date = timezone.localdate() + timedelta(days=365)

    def _activate(self, student=None, school_name="Sunnyvale Chinese School", end_date=None):
        return self.client.post(
            reverse("manager_school_subscription_activate"),
            {
                "student_id": str((student or self.student).id),
                "school_name": school_name,
                "end_date": (end_date or self.end_date).isoformat(),
            },
        )

    def test_manager_activation_grants_base_access_and_plus_gate(self):
        response = self._activate()
        self.assertRedirects(response, reverse("manager_school_subscriptions"), fetch_redirect_response=False)

        subscription = Subscription.objects.get(user=self.student)
        self.assertEqual(subscription.subscription_plan, "standard")
        self.assertEqual(subscription.subscription_cost, Decimal("15.00"))
        self.assertTrue(subscription.is_active)
        self.assertFalse(subscription.is_cancelled)
        self.assertEqual(subscription.payment_source, "school")
        self.assertEqual(subscription.school_name, "Sunnyvale Chinese School")
        self.assertEqual(subscription.activated_by, self.manager)
        self.assertIsNotNone(subscription.activated_at)
        self.assertEqual(timezone.localtime(subscription.access_until).date(), self.end_date)

        self.assertTrue(has_base_access(self.student))
        # The existing Plus upgrade view gates on exactly this condition.
        self.assertTrue(subscription.is_active and not subscription.is_cancelled)

    def test_activation_refuses_active_individual_stripe_subscription(self):
        existing = Subscription.objects.create(
            user=self.student,
            subscription_plan="standard",
            subscription_cost=15.00,
            stripe_subscription_id="sub_existing_123",
            is_active=True,
        )
        response = self._activate()
        self.assertRedirects(response, reverse("manager_school_subscriptions"), fetch_redirect_response=False)

        existing.refresh_from_db()
        self.assertEqual(existing.payment_source, "individual")
        self.assertEqual(existing.school_name, "")
        self.assertIsNone(existing.access_until)
        self.assertIsNone(existing.activated_by)

    def test_activation_refuses_disputed_student(self):
        Subscription.objects.create(
            user=self.student,
            subscription_plan="standard",
            subscription_cost=15.00,
            is_active=False,
            is_disputed=True,
            dispute_status="under_review",
        )
        self._activate()
        subscription = Subscription.objects.get(user=self.student)
        self.assertEqual(subscription.payment_source, "individual")
        self.assertFalse(subscription.is_active)

    def test_school_student_gets_school_renewal_reminder_not_auto_renew(self):
        access_until = timezone.make_aware(
            datetime.combine(timezone.localdate() + timedelta(days=7), dt_time(12, 0)),
            timezone.get_current_timezone(),
        )
        Subscription.objects.create(
            user=self.student,
            subscription_plan="standard",
            subscription_cost=15.00,
            is_active=True,
            access_until=access_until,
            payment_source="school",
            school_name="Sunnyvale Chinese School",
        )

        mail.outbox.clear()  # ignore any account-creation emails from setUp
        call_command("send_subscription_reminders")

        notification = Notification.objects.get(
            user=self.student, title="PandaSpeak Subscription Renewal Reminder"
        )
        self.assertIn("Sunnyvale Chinese School", notification.message)
        self.assertNotIn("renew automatically", notification.message)

        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, [self.student.email])
        self.assertIn("Sunnyvale Chinese School", mail.outbox[0].body)
        self.assertIn("no automatic renewal", mail.outbox[0].body)
        self.assertNotIn("renew automatically", mail.outbox[0].body)

    def test_deactivate_turns_access_off_but_keeps_history(self):
        self._activate()
        subscription = Subscription.objects.get(user=self.student)
        self.assertTrue(has_base_access(self.student))

        response = self.client.post(
            reverse("manager_school_subscription_deactivate"),
            {"subscription_id": str(subscription.pk)},
        )
        self.assertRedirects(response, reverse("manager_school_subscriptions"), fetch_redirect_response=False)

        subscription.refresh_from_db()
        self.assertFalse(subscription.is_active)
        self.assertEqual(subscription.payment_source, "school")
        self.assertEqual(subscription.school_name, "Sunnyvale Chinese School")
        fresh_student = User.objects.get(pk=self.student.pk)
        self.assertFalse(has_base_access(fresh_student))

    def test_school_page_is_staff_only(self):
        self.client.force_login(self.student)
        response = self.client.get(reverse("manager_school_subscriptions"))
        self.assertEqual(response.status_code, 302)
