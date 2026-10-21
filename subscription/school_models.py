from decimal import Decimal
from datetime import timedelta
from django.conf import settings
from django.db import models, transaction
from django.utils import timezone
from subscription.models import Subscription


class SchoolSubscriptionBatch(models.Model):
    """School-paid annual memberships; never activate before confirmed receipt."""
    school_name = models.CharField(max_length=200)
    payment_method = models.CharField(max_length=20, choices=[("card", "Credit card"), ("cash", "Cash"), ("wire", "Wire transfer")])
    amount_received = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0.00"))
    unit_price = models.DecimalField(max_digits=8, decimal_places=2, default=Decimal("15.00"))
    payment_reference = models.CharField(max_length=200, blank=True)
    payment_received_at = models.DateTimeField(null=True, blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    created_at = models.DateTimeField(auto_now_add=True)

    def activate_student(self, student):
        if not self.payment_received_at:
            raise ValueError("Payment must be received before activation.")
        if student.is_teacher or student.is_staff or not student.is_active:
            raise ValueError("Only active student accounts may be enrolled.")
        with transaction.atomic():
            batch = SchoolSubscriptionBatch.objects.select_for_update().get(pk=self.pk)
            if not batch.payment_received_at:
                raise ValueError("Payment has not been confirmed.")
            enrollment, created = SchoolSubscriptionEnrollment.objects.get_or_create(batch=batch, student=student)
            if not created:
                return enrollment
            if SchoolSubscriptionEnrollment.objects.filter(batch=batch).count() * batch.unit_price > batch.amount_received:
                raise ValueError("Insufficient confirmed funds for another student.")
            subscription, _ = Subscription.objects.select_for_update().get_or_create(
                user=student, defaults={"subscription_plan": "Standard", "subscription_cost": batch.unit_price}
            )
            if subscription.is_disputed:
                raise ValueError("Disputed accounts cannot be activated.")
            if subscription.stripe_subscription_id or subscription.paypal_subscription_id:
                raise ValueError("Student has a provider-managed annual subscription.")
            start = max(timezone.now(), subscription.access_until) if subscription.access_until else timezone.now()
            subscription.access_until = start + timedelta(days=365)
            subscription.is_active = True
            subscription.is_cancelled = False
            subscription.subscription_plan = "Standard"
            subscription.subscription_cost = batch.unit_price
            subscription.save()
            enrollment.access_until = subscription.access_until
            enrollment.save(update_fields=["access_until"])
            return enrollment


class SchoolSubscriptionEnrollment(models.Model):
    batch = models.ForeignKey(SchoolSubscriptionBatch, on_delete=models.PROTECT, related_name="enrollments")
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    access_until = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [models.UniqueConstraint(fields=["batch", "student"], name="unique_school_batch_student")]
