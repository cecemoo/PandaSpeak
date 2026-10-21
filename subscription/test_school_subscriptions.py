from datetime import timedelta
from decimal import Decimal
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from django.test import TestCase
from django.utils import timezone
from subscription.models import Subscription
from subscription.plan_access import has_base_access, is_plus
from subscription.subscription_guard_views import _has_current_subscription
from subscription.school_models import SchoolAccount, SchoolEnrollment, SchoolPayment

User = get_user_model()


class SchoolSubscriptionTests(TestCase):
    def setUp(self):
        self.student = User.objects.create_user(email="schoolstudent@example.com", password="testpassword")
        self.school = SchoolAccount.objects.create(name="Test School")
        self.start = timezone.now() - timedelta(days=1)
        self.end = timezone.now() + timedelta(days=364)

    def enroll(self):
        payment = SchoolPayment.objects.create(school=self.school, method="cash", amount=Decimal("15.00"), reference="TEST-RECEIPT", received_at=timezone.now())
        return SchoolEnrollment.objects.create(
            school=self.school, student=self.student, starts_at=self.start,
            expires_at=self.end, agreed_price=self.school.annual_price, payment=payment, payment_reference="cash:TEST-RECEIPT",
        )

    def test_anonymous_user_has_no_subscription_access(self):
        self.assertFalse(has_base_access(AnonymousUser()))

    def test_inactive_school_student_has_no_access(self):
        self.enroll()
        self.student.is_active = False
        self.student.save(update_fields=["is_active"])
        self.assertFalse(has_base_access(self.student))

    def test_reversed_school_payment_revokes_access(self):
        enrollment = self.enroll()
        self.assertTrue(has_base_access(self.student))
        payment = enrollment.payment
        payment.reversed_at = timezone.now()
        payment.save(update_fields=["reversed_at"])
        self.assertFalse(has_base_access(self.student))

    def test_pending_payment_never_grants_access(self):
        payment = SchoolPayment.objects.create(
            school=self.school, method="card", amount=Decimal("15.00"),
            stripe_session_id="cs_test_pending",
        )
        SchoolEnrollment.objects.create(
            school=self.school, student=self.student, starts_at=self.start,
            expires_at=self.end, agreed_price=Decimal("15.00"),
            payment=payment, payment_reference="card:cs_test_pending",
        )
        self.assertFalse(has_base_access(self.student))

    def test_default_and_historical_price(self):
        record = self.enroll()
        self.assertEqual(record.agreed_price, Decimal("15.00"))
        self.school.annual_price = Decimal("20.00")
        self.school.save()
        record.refresh_from_db()
        self.assertEqual(record.agreed_price, Decimal("15.00"))

    def test_school_enrollment_grants_standard_not_plus(self):
        self.enroll()
        self.assertTrue(has_base_access(self.student))
        self.assertTrue(_has_current_subscription(self.student))
        self.assertFalse(is_plus(self.student))

    def test_revoked_or_expired_enrollment_does_not_grant_access(self):
        record = self.enroll()
        record.revoked_at = timezone.now()
        record.save()
        self.assertFalse(has_base_access(self.student))
        record.revoked_at = None
        record.expires_at = timezone.now() - timedelta(seconds=1)
        record.save()
        self.assertFalse(has_base_access(self.student))

    def test_disputed_student_is_blocked_despite_school_enrollment(self):
        self.enroll()
        Subscription.objects.create(
            user=self.student, subscription_plan="standard",
            subscription_cost=Decimal("15.00"), is_disputed=True,
        )
        self.assertFalse(has_base_access(self.student))
        self.assertFalse(_has_current_subscription(self.student))

    def test_non_manager_cannot_assign_enrollment(self):
        self.client.force_login(self.student)
        response = self.client.get("/subscription/manager/schools/")
        self.assertNotEqual(response.status_code, 200)

    def test_manager_assigns_registered_student(self):
        manager = User.objects.create_user(email="manager-school@example.com", password="testpassword", is_staff=True)
        payment = SchoolPayment.objects.create(school=self.school, method="wire", amount=Decimal("15.00"),
            reference="WIRE-1", received_at=timezone.now(), confirmed_by=manager)
        self.client.force_login(manager)
        response = self.client.post("/subscription/manager/schools/", {
            "action": "enroll", "enrollment-school": str(self.school.pk),
            "enrollment-student_email": self.student.email,
            "enrollment-starts_at": timezone.localdate().isoformat(),
            "enrollment-expires_at": (timezone.localdate() + timedelta(days=365)).isoformat(),
            "enrollment-payment": str(payment.pk),
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(SchoolEnrollment.objects.filter(student=self.student, payment=payment).exists())

    def test_unpaid_school_enrollment_cannot_be_activated(self):
        manager = User.objects.create_user(email="unpaid-manager@example.com", password="testpassword", is_staff=True)
        payment = SchoolPayment.objects.create(school=self.school, method="wire", amount=Decimal("15.00"), reference="PENDING")
        self.client.force_login(manager)
        response = self.client.post("/subscription/manager/schools/", {
            "action": "enroll", "enrollment-school": str(self.school.pk),
            "enrollment-student_email": self.student.email,
            "enrollment-starts_at": timezone.localdate().isoformat(),
            "enrollment-expires_at": (timezone.localdate() + timedelta(days=365)).isoformat(),
            "enrollment-payment": str(payment.pk),
        })
        self.assertEqual(response.status_code, 200)
        self.assertFalse(has_base_access(self.student))

    def test_cash_payment_can_be_manager_confirmed(self):
        manager = User.objects.create_user(email="cash-manager@example.com", password="testpassword", is_staff=True)
        self.client.force_login(manager)
        response = self.client.post("/subscription/manager/schools/", {
            "action": "payment", "payment-school": str(self.school.pk),
            "payment-method": "cash", "payment-amount": "30.00",
            "payment-reference": "RECEIPT-100", "payment-received": "on",
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(SchoolPayment.objects.filter(school=self.school, method="cash",
            reference="RECEIPT-100", received_at__isnull=False).exists())

    def test_unconfirmed_wire_cannot_grant_access(self):
        manager = User.objects.create_user(email="wire-manager@example.com", password="testpassword", is_staff=True)
        self.client.force_login(manager)
        response = self.client.post("/subscription/manager/schools/", {
            "action": "payment", "payment-school": str(self.school.pk),
            "payment-method": "wire", "payment-amount": "15.00",
            "payment-reference": "PENDING",
        })
        self.assertEqual(response.status_code, 200)
        self.assertFalse(SchoolPayment.objects.filter(reference="PENDING").exists())

    def test_card_payment_cannot_be_manually_confirmed(self):
        from subscription.school_views import SchoolPaymentForm
        form = SchoolPaymentForm(data={
            "school": self.school.pk, "method": "card", "amount": "15.00",
            "reference": "unverified", "received": True,
        })
        self.assertTrue(form.is_valid())
        self.assertFalse(SchoolPayment.objects.exists())

    def test_overlapping_school_enrollment_rejected(self):
        self.enroll()
        from subscription.school_views import EnrollmentForm
        form = EnrollmentForm(data={
            "school": self.school.pk,
            "student_email": self.student.email,
            "starts_at": timezone.localdate().isoformat(),
            "expires_at": (timezone.localdate() + timedelta(days=365)).isoformat(),
        })
        self.assertFalse(form.is_valid())
        self.assertIn("overlapping", str(form.errors).lower())

    def test_school_inactive_blocks_access(self):
        self.enroll()
        self.school.is_active = False
        self.school.save(update_fields=["is_active"])
        self.assertFalse(has_base_access(self.student))

    def test_school_starts_in_future_does_not_grant_access(self):
        record = self.enroll()
        record.starts_at = timezone.now() + timedelta(days=1)
        record.save(update_fields=["starts_at"])
        self.assertFalse(has_base_access(self.student))

    def test_school_expiration_does_not_remove_independent_paid_access(self):
        record = self.enroll()
        Subscription.objects.create(
            user=self.student, subscription_plan="standard",
            subscription_cost=Decimal("15.00"), is_active=True,
            access_until=timezone.now() + timedelta(days=30),
        )
        record.revoked_at = timezone.now()
        record.save(update_fields=["revoked_at"])
        self.assertTrue(has_base_access(self.student))

    def test_school_enrollment_does_not_bypass_dispute_after_activation(self):
        record = self.enroll()
        self.assertTrue(has_base_access(self.student))
        Subscription.objects.create(
            user=self.student, subscription_plan="standard",
            subscription_cost=Decimal("15.00"), is_disputed=True,
        )
        self.assertFalse(has_base_access(self.student))
        self.assertIsNone(record.revoked_at)
