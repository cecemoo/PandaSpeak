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
