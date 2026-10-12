"""Server-side purchase restrictions. Keep personal identifiers in server environment variables."""
import os
from django.contrib import messages
from django.shortcuts import redirect
from .models import Subscription


def purchase_blocked_response(request):
    """Return a redirect for a blocked signed-in purchaser, otherwise None."""
    user = request.user
    if not user.is_authenticated:
        return redirect("login")
    email = (user.email or "").strip().casefold()
    blocked_emails = {v.strip().casefold() for v in os.environ.get("PANDA_BLOCKED_EMAILS", "").split(",") if v.strip()}
    subscription = Subscription.objects.filter(user=user).first()
    # Stripe customer IDs are not stored on the Subscription model yet.
    # Check the confirmed email and local dispute flag until that mapping exists.
    if ((subscription and subscription.is_disputed)
            or (email and email in blocked_emails)
            ):
        messages.error(request, "This account is not eligible to make purchases.")
        return redirect("dispute_restricted")
    return None
