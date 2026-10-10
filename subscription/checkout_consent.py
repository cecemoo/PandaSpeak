"""Server-side subscription checkout acknowledgement (not just a browser checkbox)."""
from django.contrib import messages
from django.shortcuts import redirect
from django.utils import timezone

from .models import Subscription

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
    return None
