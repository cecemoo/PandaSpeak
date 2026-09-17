from datetime import datetime, timezone

import stripe
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.views.decorators.csrf import csrf_exempt

from .models import Subscription


User = get_user_model()


def _subscription_api_key():
    return getattr(settings, "STRIPE_SUBSCRIPTION_SECRET_KEY", "") or settings.STRIPE_SECRET_KEY


def _stripe_value(obj, key, default=None):
    """Read a value from either a dict or a Stripe object safely."""
    if obj is None:
        return default
    if isinstance(obj, dict):
        return obj.get(key, default)
    try:
        return getattr(obj, key)
    except (AttributeError, KeyError, TypeError):
        return default


def _annual_line_items():
    price_id = getattr(settings, "STRIPE_SUBSCRIPTION_PRICE_ID", "")
    if price_id:
        return [{"price": price_id, "quantity": 1}]

    # Safe fallback so production checkout keeps working until the live Price ID
    # is added to the server environment.
    return [
        {
            "price_data": {
                "currency": "usd",
                "product_data": {
                    "name": "PandaSpeak Annual Subscription",
                    "description": "Annual access to PandaSpeak Chinese learning materials.",
                },
                "unit_amount": 1500,
                "recurring": {"interval": "year"},
            },
            "quantity": 1,
        }
    ]


@login_required
def stripe_subscription_checkout(request):
    if request.method != "POST":
        return redirect("subscribe")

    # Do not create another Stripe subscription Checkout for a user who already
    # has an active PandaSpeak subscription. This prevents accidental duplicate
    # subscriptions/charges from repeated clicks or revisiting the subscribe page.
    existing = Subscription.objects.filter(user=request.user).first()
    if existing and existing.is_active and not existing.is_cancelled:
        messages.info(
            request,
            "You already have an active PandaSpeak subscription. No additional payment was created.",
        )
        return redirect("student_dashboard")

    api_key = _subscription_api_key()
    if not api_key:
        messages.error(request, "Card subscription checkout is not configured yet.")
        return redirect("subscribe")

    try:
        checkout_session = stripe.checkout.Session.create(
            api_key=api_key,
            mode="subscription",
            payment_method_types=["card"],
            customer_email=request.user.email or None,
            line_items=_annual_line_items(),
            success_url=(
                request.build_absolute_uri("/subscription/stripe/success/")
                + "?session_id={CHECKOUT_SESSION_ID}"
            ),
            cancel_url=request.build_absolute_uri("/subscription/subscribe/"),
            metadata={
                "purpose": "pandaspeak_annual_subscription",
                "user_id": str(request.user.id),
            },
            subscription_data={
                "metadata": {
                    "purpose": "pandaspeak_annual_subscription",
                    "user_id": str(request.user.id),
                }
            },
        )
        return redirect(checkout_session.url)
    except stripe.error.StripeError:
        messages.error(request, "Unable to start card checkout right now. Please try again.")
        return redirect("subscribe")


def _period_end_datetime(stripe_subscription):
    period_end = _stripe_value(stripe_subscription, "current_period_end")
    if not period_end:
        return None
    return datetime.fromtimestamp(period_end, tz=timezone.utc)


def _sync_subscription_from_stripe(stripe_subscription, user=None):
    metadata = _stripe_value(stripe_subscription, "metadata", {}) or {}
    if _stripe_value(metadata, "purpose") != "pandaspeak_annual_subscription":
        return

    stripe_subscription_id = _stripe_value(stripe_subscription, "id")
    if not stripe_subscription_id:
        return

    status = _stripe_value(stripe_subscription, "status")
    cancel_at_period_end = bool(_stripe_value(stripe_subscription, "cancel_at_period_end", False))

    local_subscription = Subscription.objects.filter(
        stripe_subscription_id=stripe_subscription_id
    ).first()

    if local_subscription is None:
        if user is None:
            user_id = _stripe_value(metadata, "user_id")
            if not user_id:
                return
            try:
                user = User.objects.get(pk=user_id)
            except (User.DoesNotExist, ValueError, TypeError):
                return

        existing = Subscription.objects.filter(user=user).first()
        if existing is not None:
            # A Stripe event for a different subscription must never overwrite a
            # currently active PandaSpeak subscription. This protects a valid
            # subscription when an accidental duplicate is cancelled/refunded.
            if (
                existing.stripe_subscription_id
                and existing.stripe_subscription_id != stripe_subscription_id
                and existing.is_active
                and not existing.is_cancelled
            ):
                return
            local_subscription = existing
        else:
            local_subscription = Subscription.objects.create(
                user=user,
                subscription_plan="standard",
                subscription_cost=15.00,
            )

    local_subscription.subscription_plan = "standard"
    local_subscription.subscription_cost = 15.00
    local_subscription.paypal_subscription_id = None
    local_subscription.stripe_subscription_id = stripe_subscription_id
    local_subscription.is_active = status in ("active", "trialing")
    local_subscription.is_cancelled = cancel_at_period_end or status in ("canceled", "unpaid", "incomplete_expired")
    local_subscription.access_until = _period_end_datetime(stripe_subscription)
    local_subscription.save()


@login_required
def stripe_subscription_success(request):
    session_id = request.GET.get("session_id", "")
    if not session_id:
        messages.error(request, "Stripe did not return a checkout session ID.")
        return redirect("subscribe")

    try:
        checkout_session = stripe.checkout.Session.retrieve(
            session_id,
            api_key=_subscription_api_key(),
        )
    except stripe.error.StripeError:
        messages.error(request, "We could not verify your card subscription. Please contact PandaSpeak support if you were charged.")
        return redirect("subscribe")

    metadata = _stripe_value(checkout_session, "metadata", {}) or {}
    subscription_id = _stripe_value(checkout_session, "subscription")
    if (
        _stripe_value(checkout_session, "mode") != "subscription"
        or _stripe_value(metadata, "purpose") != "pandaspeak_annual_subscription"
        or str(_stripe_value(metadata, "user_id")) != str(request.user.id)
        or _stripe_value(checkout_session, "payment_status") not in ("paid", "no_payment_required")
        or not subscription_id
    ):
        messages.error(request, "We could not verify your card subscription. Please contact PandaSpeak support if you were charged.")
        return redirect("subscribe")

    try:
        stripe_subscription = stripe.Subscription.retrieve(
            subscription_id,
            api_key=_subscription_api_key(),
        )
        _sync_subscription_from_stripe(stripe_subscription, user=request.user)
    except stripe.error.StripeError:
        messages.error(request, "Your payment completed, but PandaSpeak could not finish verification yet. Please contact support if access is not enabled.")
        return redirect("subscribe")

    return render(
        request,
        "subscription/success.html",
        {"user": request.user, "first_name": request.user.first_name},
    )


@csrf_exempt
def stripe_subscription_webhook(request):
    if request.method != "POST":
        return HttpResponse(status=405)

    webhook_secret = getattr(settings, "STRIPE_SUBSCRIPTION_WEBHOOK_SECRET", "")
    if not webhook_secret:
        return HttpResponse("Subscription webhook secret is not configured.", status=503)

    payload = request.body
    signature = request.META.get("HTTP_STRIPE_SIGNATURE", "")

    try:
        event = stripe.Webhook.construct_event(payload, signature, webhook_secret)
    except (ValueError, stripe.error.SignatureVerificationError):
        return HttpResponse(status=400)

    event_type = _stripe_value(event, "type")
    event_data = _stripe_value(event, "data", {}) or {}
    obj = _stripe_value(event_data, "object", {}) or {}

    try:
        if event_type == "checkout.session.completed":
            metadata = _stripe_value(obj, "metadata", {}) or {}
            subscription_id = _stripe_value(obj, "subscription")
            if (
                _stripe_value(obj, "mode") == "subscription"
                and _stripe_value(metadata, "purpose") == "pandaspeak_annual_subscription"
                and subscription_id
            ):
                user_id = _stripe_value(metadata, "user_id")
                try:
                    user = User.objects.get(pk=user_id)
                except (User.DoesNotExist, ValueError, TypeError):
                    return HttpResponse(status=200)

                stripe_subscription = stripe.Subscription.retrieve(
                    subscription_id,
                    api_key=_subscription_api_key(),
                )
                _sync_subscription_from_stripe(stripe_subscription, user=user)

        elif event_type in ("customer.subscription.created", "customer.subscription.updated", "customer.subscription.deleted"):
            _sync_subscription_from_stripe(obj)

        elif event_type in ("invoice.paid", "invoice.payment_failed"):
            stripe_subscription_id = _stripe_value(obj, "subscription")
            if stripe_subscription_id:
                stripe_subscription = stripe.Subscription.retrieve(
                    stripe_subscription_id,
                    api_key=_subscription_api_key(),
                )
                _sync_subscription_from_stripe(stripe_subscription)

    except stripe.error.StripeError:
        # Return 500 so Stripe retries transient API failures.
        return HttpResponse(status=500)

    return HttpResponse(status=200)
