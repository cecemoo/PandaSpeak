from time import timezone
from django.db import models
from django.conf import settings
from account.models import CustomUser



class Subscription(models.Model):
    subscription_plan = models.CharField(max_length=300)
    subscription_cost = models.DecimalField(max_digits=8, decimal_places=2)
    paypal_subscription_id = models.CharField(max_length=300, blank=True, null=True)
    is_active = models.BooleanField(default=False)
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, unique=True)
    is_cancelled = models.BooleanField(default=False)
    access_until = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f"{self.user} - {self.subscription_plan} subscription" 



class TutoringPayment(models.Model):
    student_name = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="student_payments")
    teacher_name = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="teacher_payments", blank=True, null=True)
    stripe_payment_id = models.CharField(max_length=300, blank=True, null=True)
    class_name = models.CharField(max_length=300)
    amount = models.DecimalField(max_digits=8, decimal_places=2)
    is_paid = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    platform_fee_percent = models.DecimalField(max_digits=5, decimal_places=2, default=20.00)


    def __str__(self):
        return f"{self.student_name} - {self.class_name} payment"
