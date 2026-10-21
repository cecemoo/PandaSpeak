from decimal import Decimal
from django.test import TestCase
from django.utils import timezone
from account.models import CustomUser
from subscription.models import SchoolSubscriptionBatch, SchoolSubscriptionEnrollment, Subscription


class SchoolSubscriptionTests(TestCase):
    def setUp(self):
        self.manager = CustomUser.objects.create_user(email="manager-school@example.com", password="test-pass", first_name="Manager", last_name="Test")
        self.student = CustomUser.objects.create_user(email="student-school@example.com", password="test-pass", first_name="Student", last_name="Test")
        self.batch = SchoolSubscriptionBatch.objects.create(school_name="Example School", payment_method="wire", amount_received=Decimal("15.00"), unit_price=Decimal("15.00"), created_by=self.manager)

    def test_no_activation_before_receipt(self):
        with self.assertRaises(ValueError):
            self.batch.activate_student(self.student)
        self.assertFalse(Subscription.objects.filter(user=self.student, is_active=True).exists())

    def test_confirmed_payment_enrolls_once(self):
        self.batch.payment_received_at = timezone.now()
        self.batch.save()
        first = self.batch.activate_student(self.student)
        second = self.batch.activate_student(self.student)
        self.assertEqual(first.pk, second.pk)
        self.assertEqual(SchoolSubscriptionEnrollment.objects.filter(batch=self.batch).count(), 1)
        self.assertTrue(Subscription.objects.get(user=self.student).is_active)

    def test_cannot_enroll_more_than_paid(self):
        self.batch.payment_received_at = timezone.now()
        self.batch.save()
        self.batch.activate_student(self.student)
        other = CustomUser.objects.create_user(email="other-school@example.com", password="test-pass", first_name="Other", last_name="Test")
        with self.assertRaises(ValueError):
            self.batch.activate_student(other)
        self.assertFalse(Subscription.objects.filter(user=other, is_active=True).exists())

    def test_disputed_student_is_not_enrolled(self):
        self.batch.payment_received_at = timezone.now()
        self.batch.save()
        Subscription.objects.create(user=self.student, subscription_plan="Standard", subscription_cost=Decimal("15.00"), is_disputed=True)
        with self.assertRaises(ValueError):
            self.batch.activate_student(self.student)
        self.assertFalse(SchoolSubscriptionEnrollment.objects.filter(student=self.student).exists())

    def test_existing_provider_subscription_not_replaced(self):
        self.batch.payment_received_at = timezone.now()
        self.batch.save()
        Subscription.objects.create(user=self.student, subscription_plan="Standard", subscription_cost=Decimal("15.00"), stripe_subscription_id="sub_existing")
        with self.assertRaises(ValueError):
            self.batch.activate_student(self.student)
        self.assertFalse(SchoolSubscriptionEnrollment.objects.filter(student=self.student).exists())
