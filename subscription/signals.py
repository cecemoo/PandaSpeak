from django.contrib.auth import get_user_model
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.urls import reverse

from account.models import Notification
from account.push import send_push_to_user
from .models import Subscription


@receiver(pre_save, sender=Subscription)
def mark_subscription_activation(sender, instance, **kwargs):
    """Track whether this save changes a subscription from inactive to active."""
    if not instance.pk:
        instance._became_active = bool(instance.is_active)
        return

    previous_is_active = (
        Subscription.objects.filter(pk=instance.pk)
        .values_list("is_active", flat=True)
        .first()
    )
    instance._became_active = bool(instance.is_active and not previous_is_active)


@receiver(post_save, sender=Subscription)
def notify_managers_on_subscription(sender, instance, created, **kwargs):
    """Notify PandaSpeak managers when a student becomes an active subscriber."""
    if not getattr(instance, "_became_active", False):
        return

    student = instance.user
    student_name = student.get_full_name() or student.email or student.username

    if instance.stripe_subscription_id:
        payment_method = "Stripe"
    elif instance.paypal_subscription_id:
        payment_method = "PayPal"
    else:
        payment_method = "online payment"

    title = "New Student Subscription"
    message = (
        f"{student_name} ({student.email}) subscribed to the PandaSpeak "
        f"annual plan via {payment_method}."
    )
    link = reverse("manager_dashboard")

    User = get_user_model()
    managers = User.objects.filter(is_staff=True, is_active=True)

    for manager in managers:
        Notification.objects.create(
            user=manager,
            title=title,
            message=message,
            link=link,
        )
        send_push_to_user(manager, title, message, link)
