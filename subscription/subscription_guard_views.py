from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.utils import timezone

from .models import Subscription
from . import views
from . import stripe_subscription_views
from . import paypal_subscription_views


def _has_current_subscription(user):
    """Return True while the user already has paid PandaSpeak access."""
    try:
        subscription = Subscription.objects.get(user=user)
    except Subscription.DoesNotExist:
        return False

    if subscription.is_disputed:
        return False

    if not subscription.is_active:
        return False

    if subscription.is_cancelled and subscription.access_until:
        return subscription.access_until > timezone.now()

    return True


def _is_disputed(user):
    return Subscription.objects.filter(user=user, is_disputed=True).exists()


def _already_subscribed_response(request):
    messages.info(
        request,
        "You already have an active PandaSpeak subscription. "
        "A second subscription cannot be created while your current subscription is active.",
    )
    return redirect("account_management_student")


def _disputed_response(request):
    messages.error(
        request,
        "This account cannot purchase or access PandaSpeak learning materials while a payment dispute is recorded.",
    )
    return redirect("dispute_restricted")


@login_required
def dispute_restricted(request):
    return render(request, "subscription/dispute_restricted.html")


@login_required
def guarded_subscribe(request):
    """Protect PayPal and Stripe subscription entry points from duplicates and disputes."""
    if _is_disputed(request.user):
        return _disputed_response(request)
    if _has_current_subscription(request.user):
        return _already_subscribed_response(request)
    if request.method == "POST" and request.POST.get("payment_method", "paypal") == "paypal":
        return paypal_subscription_views.paypal_subscription_checkout(request)
    return views.subscribe(request)


@login_required
def guarded_stripe_subscription_checkout(request):
    """Protect the dedicated Stripe checkout URL from duplicate or disputed accounts."""
    if _is_disputed(request.user):
        return _disputed_response(request)
    if _has_current_subscription(request.user):
        return _already_subscribed_response(request)
    return stripe_subscription_views.stripe_subscription_checkout(request)
