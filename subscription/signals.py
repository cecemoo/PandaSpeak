from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.urls import reverse

from account.models import Notification
from account.push import send_push_to_user
from .models import Subscription


def _payment_method(subscription):
    if subscription.stripe_subscription_id:
        return "Stripe"
    if subscription.paypal_subscription_id:
        return "PayPal"
    return "online payment"


def _manager_queryset():
    User = get_user_model()
    return User.objects.filter(is_staff=True, is_active=True)


@receiver(pre_save, sender=Subscription)
def mark_subscription_changes(sender, instance, **kwargs):
    if not instance.pk:
        instance._became_active = bool(instance.is_active)
        instance._became_cancelled = bool(instance.is_cancelled)
        return
    previous = Subscription.objects.filter(pk=instance.pk).values("is_active", "is_cancelled").first() or {"is_active": False, "is_cancelled": False}
    instance._became_active = bool(instance.is_active and not previous["is_active"])
    instance._became_cancelled = bool(instance.is_cancelled and not previous["is_cancelled"])


@receiver(post_save, sender=Subscription)
def notify_managers_on_subscription(sender, instance, created, **kwargs):
    became_active = getattr(instance, "_became_active", False)
    became_cancelled = getattr(instance, "_became_cancelled", False)
    if not became_active and not became_cancelled:
        return

    student = instance.user
    student_name = student.get_full_name() or student.email or student.username
    payment_method = _payment_method(instance)
    link = reverse("manager_dashboard")
    managers = _manager_queryset()

    if became_active:
        # Payment-provider code only changes is_active after verified annual activation.
        # Keep referral awarding here so Stripe, ACH and PayPal share one idempotent path.
        from .referrals import activate_next_free_month, grant_referral_rewards
        if grant_referral_rewards(student):
            activate_next_free_month(student)
            referral = getattr(student, "referral_received", None)
            if referral:
                activate_next_free_month(referral.referrer)

        if student.email:
            greeting_name = student.first_name or student.get_full_name() or "Student"
            access_text = instance.access_until.strftime("%b %d, %Y") if instance.access_until else None
            access_line = f"\nYour current subscription period is active through {access_text}." if access_text else ""
            send_mail(subject="Your PandaSpeak Subscription Is Active", message=(f"Dear {greeting_name},\n\nGood news! Your PandaSpeak subscription payment has been confirmed. Your subscription is now active, and you can access the PandaSpeak learning materials.{access_line}\n\nThank you for subscribing to PandaSpeak.\n\nPandaSpeak Team"), from_email=settings.DEFAULT_FROM_EMAIL, recipient_list=[student.email], fail_silently=True)

        title = "New Student Subscription"
        message = f"{student_name} ({student.email}) subscribed to the PandaSpeak annual plan via {payment_method}."
        for manager in managers:
            Notification.objects.create(user=manager, title=title, message=message, link=link)
            send_push_to_user(manager, title, message, link)
        manager_emails = list(managers.exclude(email="").values_list("email", flat=True).distinct())
        if manager_emails:
            send_mail(subject="New PandaSpeak Student Subscription", message=(f"A student subscription has been activated on PandaSpeak.\n\nStudent: {student_name}\nEmail: {student.email}\nPlan: Annual\nPayment method: {payment_method}\n"), from_email=settings.DEFAULT_FROM_EMAIL, recipient_list=manager_emails, fail_silently=True)

    if became_cancelled:
        title = "Student Subscription Cancelled"
        access_text = instance.access_until.strftime("%b %d, %Y") if instance.access_until else "the end of the current paid period"
        message = f"{student_name} ({student.email}) cancelled the PandaSpeak annual subscription via {payment_method}. Access remains available until {access_text}."
        for manager in managers:
            Notification.objects.create(user=manager, title=title, message=message, link=link)
            send_push_to_user(manager, title, message, link)
        manager_emails = list(managers.exclude(email="").values_list("email", flat=True).distinct())
        if manager_emails:
            send_mail(subject="PandaSpeak Student Subscription Cancelled", message=(f"A student has cancelled a PandaSpeak subscription.\n\nStudent: {student_name}\nEmail: {student.email}\nPlan: Annual\nPayment method: {payment_method}\nAccess until: {access_text}\n\nThe student should retain access through the current paid period and will not renew automatically."), from_email=settings.DEFAULT_FROM_EMAIL, recipient_list=manager_emails, fail_silently=True)
