from unittest.mock import Mock, patch

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import Subscription
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
        response = self.client.post(reverse("stripe_subscription_checkout"))
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
        response = self.client.post(reverse("stripe_subscription_checkout"))
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
        response = self.client.post(reverse("stripe_subscription_checkout"))
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
                "accept_subscription_terms": "yes"
            })
        self.assertEqual(response.status_code, 302)
        subscription = Subscription.objects.get(user=self.user)
        self.assertIsNotNone(subscription.checkout_terms_accepted_at)
        self.assertEqual(subscription.checkout_terms_version, "2026-10-10")
