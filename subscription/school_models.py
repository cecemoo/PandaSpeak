from decimal import Decimal
from django.conf import settings
from django.db import models


class SchoolAccount(models.Model):
    name = models.CharField(max_length=200, unique=True)
    contact_email = models.EmailField(blank=True)
    annual_price = models.DecimalField(max_digits=8, decimal_places=2, default=Decimal('15.00'))
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class SchoolEnrollment(models.Model):
    school = models.ForeignKey(SchoolAccount, on_delete=models.PROTECT, related_name='enrollments')
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='school_enrollments')
    starts_at = models.DateTimeField()
    expires_at = models.DateTimeField()
    agreed_price = models.DecimalField(max_digits=8, decimal_places=2)
    payment_reference = models.CharField(max_length=200, blank=True)
    payment = models.ForeignKey("SchoolPayment", on_delete=models.PROTECT, null=True, blank=True, related_name="enrollments")
    revoked_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def clean(self):
        from django.core.exceptions import ValidationError
        if self.starts_at and self.expires_at and self.expires_at <= self.starts_at:
            raise ValidationError('Expiration must follow start date.')
        if not self.payment_reference or not self.payment_reference.strip():
            raise ValidationError('A received payment reference is required before activation.')


class SchoolPayment(models.Model):
    METHOD_CHOICES = (("card", "Credit card"), ("cash", "Cash"), ("wire", "Wire transfer"))
    school = models.ForeignKey(SchoolAccount, on_delete=models.PROTECT, related_name="payments")
    method = models.CharField(max_length=8, choices=METHOD_CHOICES)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    reference = models.CharField(max_length=200, blank=True)
    stripe_session_id = models.CharField(max_length=255, blank=True, unique=True, null=True)
    received_at = models.DateTimeField(null=True, blank=True)
    confirmed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def confirmed(self):
        return self.received_at is not None
