from datetime import timedelta
from decimal import Decimal
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone
from subscription.models import Subscription
from subscription.plan_access import has_base_access, is_plus
from subscription.subscription_guard_views import _has_current_subscription
from subscription.school_models import SchoolAccount, SchoolEnrollment

User = get_user_model()


class SchoolSubscriptionTests(TestCase):
    def setUp(self):
        self.student = User.objects.create_user(email="schoolstudent@example.com", password="testpassword")
        self.school = SchoolAccount.objects.create(name="Test School")
        self.start = timezone.now() - timedelta(days=1)
        self.end = timezone.now() + timedelta(days=364)

    def enroll(self):
        return SchoolEnrollment.objects.create(
            school=self.school, student=self.student, starts_at=self.start,
            expires_at=self.end, agreed_price=self.school.annual_price,
        )

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
        self.client.force_login(manager)
        response = self.client.post("/subscription/manager/schools/", {
            "action": "enroll", "enrollment-school": str(self.school.pk),
            "enrollment-student_email": self.student.email,
            "enrollment-starts_at": timezone.localdate().isoformat(),
            "enrollment-expires_at": (timezone.localdate() + timedelta(days=365)).isoformat(),
            "enrollment-payment_reference": "SCHOOL-INVOICE-1",
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(SchoolEnrollment.objects.filter(student=self.student, school=self.school).exists())
