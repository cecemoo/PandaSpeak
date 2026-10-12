"""Server-side purchase restrictions, backed by a manager-maintained database list."""
from django.contrib import messages
from django.shortcuts import redirect
from .models import BlockedPurchaseEmail, Subscription


def purchase_blocked_response(request):
    """Return a redirect for a blocked signed-in purchaser, otherwise None."""
    user = request.user
    if not user.is_authenticated:
        return redirect("my_login")
    email = (user.email or "").strip().lower()
    subscription = Subscription.objects.filter(user=user).first()
    blocked = bool(subscription and subscription.is_disputed)
    if email:
        blocked = blocked or BlockedPurchaseEmail.objects.filter(email__iexact=email).exists()
    if blocked:
        messages.error(request, "This account is not eligible to make purchases.")
        return redirect("dispute_restricted")
    return None
