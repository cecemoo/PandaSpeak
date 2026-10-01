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
    """Track activation, cancellation, and dispute transitions for notifications."""
    if not instance.pk:
        instance._became_active = bool(instance.is_active)
        instance._became_cancelled = bool(instance.is_cancelled)
        instance._became_disputed = bool(instance.is_disputed)
        return

    previous = (
        Subscription.objects.filter(pk=instance.pk)
        .values("is_active", "is_cancelled", "is_disputed")
        .first()
    ) or {"is_active": False, "is_cancelled": False, "is_disputed": False}

    instance._became_active = bool(instance.is_active and not previous["is_active"])
    instance._became_cancelled = bool(instance.is_cancelled and not previous["is_cancelled"])
    instance._became_disputed = bool(instance.is_disputed and not previous["is_disputed"])


@receiver(post_save, sender=Subscription)
def notify_managers_on_subscription(sender, instance, created, **kwargs):
    """Notify students and PandaSpeak managers about important subscription changes."""
    became_active = getattr(instance, "_became_active", False)
    became_cancelled = getattr(instance, "_became_cancelled", False)
    became_disputed = getattr(instance, "_became_disputed", False)
    if not became_active and not became_cancelled and not became_disputed:
        return

    student = instance.user
    student_name = student.get_full_name() or student.email or student.username
    payment_method = _payment_method(instance)
    link = reverse("manager_dashboard")
    managers = _manager_queryset()

    if became_active:
        # Annual activation happens only after verified payment. Award referral
        # rewards here so Stripe, delayed ACH, and PayPal share one safe path.
        from .referrals import activate_available_free_months, grant_referral_rewards

        if grant_referral_rewards(student):
            activate_available_free_months(student)
            referral = getattr(student, "referral_received", None)
            if referral:
                activate_available_free_months(referral.referrer)

        # The activation transition occurs only after the payment flow has
        # confirmed payment, so this also covers delayed ACH confirmation.
        if student.email:
            greeting_name = student.first_name or student.get_full_name() or "Student"
            access_until = instance.access_until
            access_text = access_until.strftime("%b %d, %Y") if access_until else None
            access_line = f"\nYour current subscription period is active through {access_text}." if access_text else ""
            send_mail(
                subject="Your PandaSpeak Subscription Is Active",
                message=(
                    f"Dear {greeting_name},\n\n"
                    "Good news! Your PandaSpeak subscription payment has been confirmed. "
                    "Your subscription is now active, and you can access the PandaSpeak learning materials."
                    f"{access_line}\n\n"
                    "Thank you for subscribing to PandaSpeak.\n\n"
                    "PandaSpeak Team"
                ),
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[student.email],
                fail_silently=True,
            )

        title = "New Student Subscription"
        message = (
            f"{student_name} ({student.email}) subscribed to the PandaSpeak "
            f"annual plan via {payment_method}."
        )

        for manager in managers:
            Notification.objects.create(
                user=manager,
                title=title,
                message=message,
                link=link,
            )
            send_push_to_user(manager, title, message, link)

        manager_emails = list(
            managers.exclude(email="").values_list("email", flat=True).distinct()
        )
        if manager_emails:
            send_mail(
                subject="New PandaSpeak Student Subscription",
                message=(
                    "A student subscription has been activated on PandaSpeak.\n\n"
                    f"Student: {student_name}\n"
                    f"Email: {student.email}\n"
                    "Plan: Annual\n"
                    f"Payment method: {payment_method}\n"
                ),
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=manager_emails,
                fail_silently=True,
            )

    if became_cancelled:
        title = "Student Subscription Cancelled"
        access_until = instance.access_until
        access_text = access_until.strftime("%b %d, %Y") if access_until else "the end of the current paid period"
        message = (
            f"{student_name} ({student.email}) cancelled the PandaSpeak annual "
            f"subscription via {payment_method}. Access remains available until {access_text}."
        )

        for manager in managers:
            Notification.objects.create(
                user=manager,
                title=title,
                message=message,
                link=link,
            )
            send_push_to_user(manager, title, message, link)

        manager_emails = list(
            managers.exclude(email="").values_list("email", flat=True).distinct()
        )
        if manager_emails:
            send_mail(
                subject="PandaSpeak Student Subscription Cancelled",
                message=(
                    "A student has cancelled a PandaSpeak subscription.\n\n"
                    f"Student: {student_name}\n"
                    f"Email: {student.email}\n"
                    "Plan: Annual\n"
                    f"Payment method: {payment_method}\n"
                    f"Access until: {access_text}\n\n"
                    "The student should retain access through the current paid period and will not renew automatically."
                ),
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=manager_emails,
                fail_silently=True,
            )

    if became_disputed:
        greeting_name = student.first_name or student.get_full_name() or "Student"

        if student.email:
            send_mail(
                subject="PandaSpeak Access Temporarily Suspended - Payment Dispute",
                message=(
                    f"Dear {greeting_name},\n\n"
                    "We received notice that a payment dispute has been opened with your bank or card issuer for your PandaSpeak annual subscription. "
                    "Because the disputed payment is associated with your current access to PandaSpeak learning materials, your paid learning access has been temporarily suspended while the dispute is unresolved.\n\n"
                    "If you opened the dispute by mistake and would like to resume access, please contact your bank or card issuer and ask them to withdraw or cancel the dispute. "
                    "After you have done so, please contact PandaSpeak Support at pandaspeaksupport@gmail.com. "
                    "Access will remain suspended until PandaSpeak can confirm that the dispute has been withdrawn or otherwise resolved.\n\n"
                    "If you believe this notice is an error, please contact PandaSpeak Support.\n\n"
                    "Best,\n"
                    "PandaSpeak Team"
                ),
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[student.email],
                fail_silently=True,
            )

        title = "Student Payment Dispute - Access Suspended"
        message = (
            f"{student_name} ({student.email}) opened a payment dispute for an active PandaSpeak annual subscription. "
            "Paid learning access has been suspended while the dispute is unresolved."
        )
        for manager in managers:
            Notification.objects.create(
                user=manager,
                title=title,
                message=message,
                link=link,
            )
            send_push_to_user(manager, title, message, link)
