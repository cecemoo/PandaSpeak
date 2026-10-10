"""Server-side subscription checkout acknowledgement (not just a browser checkbox)."""
from django.contrib import messages
from django.shortcuts import redirect
from django.utils import timezone

from .models import Subscription

TERMS_VERSION = "2026-10-10"


def require_checkout_consent(request):
    if request.POST.get("accept_subscription_terms") != "yes":
        messages.error(request, "Please review and acknowledge the Terms of Service and FAQ before checkout.")
        return redirect("subscribe")
    # Record an audit timestamp before sending the student to the payment provider.
    Subscription.objects.update_or_create(
        user=request.user,
        defaults={
            "checkout_terms_accepted_at": timezone.now(),
            "checkout_terms_version": TERMS_VERSION,
        },
        create_defaults={
            "subscription_plan": "standard",
            "subscription_cost": 15,
            "checkout_terms_accepted_at": timezone.now(),
            "checkout_terms_version": TERMS_VERSION,
        },
    )
    return None
