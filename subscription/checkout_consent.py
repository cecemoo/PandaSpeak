"""Server-side subscription checkout acknowledgement (not just a browser checkbox)."""
from django.contrib import messages
from django.shortcuts import redirect
from django.utils import timezone

from .models import Subscription, SubscriptionConsentEvent

TERMS_VERSION = "2026-10-10"


def require_checkout_consent(request):
    if (request.POST.get("accept_subscription_terms") != "yes"
            or request.POST.get("accept_subscription_faq") != "yes"):
        messages.error(request, "Please review and acknowledge the Terms of Service and FAQ before checkout.")
        return redirect("subscribe")
    # Record an audit timestamp before sending the student to the payment provider.
    subscription, _ = Subscription.objects.get_or_create(
        user=request.user,
        defaults={"subscription_plan": "standard", "subscription_cost": 15},
    )
    subscription.checkout_terms_accepted_at = timezone.now()
    subscription.checkout_terms_version = TERMS_VERSION
    subscription.save(update_fields=["checkout_terms_accepted_at", "checkout_terms_version"])
    SubscriptionConsentEvent.objects.create(
        user=request.user,
        terms_version=TERMS_VERSION,
        terms_accepted=True,
        faq_accepted=True,
        payment_provider=(request.POST.get("payment_method") or "stripe")[:20],
        ip_address=request.META.get("REMOTE_ADDR") or None,
        user_agent=(request.META.get("HTTP_USER_AGENT") or "")[:1000],
    )
    return None
