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
    period_end = stripe_subscription.get("current_period_end")
    if not period_end:
        return None
    return datetime.fromtimestamp(period_end, tz=timezone.utc)


def _sync_subscription_from_stripe(stripe_subscription, user=None):
    metadata = stripe_subscription.get("metadata") or {}
    if metadata.get("purpose") != "pandaspeak_annual_subscription":
        return

    stripe_subscription_id = stripe_subscription.get("id")
    if not stripe_subscription_id:
        return

    local_subscription = None
    if user is not None:
        local_subscription, _ = Subscription.objects.get_or_create(
            user=user,
            defaults={
                "subscription_plan": "standard",
                "subscription_cost": 15.00,
            },
        )
    else:
        local_subscription = Subscription.objects.filter(
            stripe_subscription_id=stripe_subscription_id
        ).first()
        if local_subscription is None:
            user_id = metadata.get("user_id")
            if user_id:
                try:
                    user = User.objects.get(pk=user_id)
                except (User.DoesNotExist, ValueError, TypeError):
                    return
                local_subscription, _ = Subscription.objects.get_or_create(
                    user=user,
                    defaults={
                        "subscription_plan": "standard",
                        "subscription_cost": 15.00,
                    },
                )

    if local_subscription is None:
        return

    status = stripe_subscription.get("status")
    cancel_at_period_end = bool(stripe_subscription.get("cancel_at_period_end"))

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

    metadata = checkout_session.get("metadata") or {}
    if (
        checkout_session.get("mode") != "subscription"
        or metadata.get("purpose") != "pandaspeak_annual_subscription"
        or str(metadata.get("user_id")) != str(request.user.id)
        or checkout_session.get("payment_status") not in ("paid", "no_payment_required")
        or not checkout_session.get("subscription")
    ):
        messages.error(request, "We could not verify your card subscription. Please contact PandaSpeak support if you were charged.")
        return redirect("subscribe")

    try:
        stripe_subscription = stripe.Subscription.retrieve(
            checkout_session.get("subscription"),
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

    event_type = event.get("type")
    obj = event.get("data", {}).get("object", {})

    try:
        if event_type == "checkout.session.completed":
            metadata = obj.get("metadata") or {}
            if (
                obj.get("mode") == "subscription"
                and metadata.get("purpose") == "pandaspeak_annual_subscription"
                and obj.get("subscription")
            ):
                user_id = metadata.get("user_id")
                try:
                    user = User.objects.get(pk=user_id)
                except (User.DoesNotExist, ValueError, TypeError):
                    return HttpResponse(status=200)

                stripe_subscription = stripe.Subscription.retrieve(
                    obj.get("subscription"),
                    api_key=_subscription_api_key(),
                )
                _sync_subscription_from_stripe(stripe_subscription, user=user)

        elif event_type in ("customer.subscription.created", "customer.subscription.updated", "customer.subscription.deleted"):
            _sync_subscription_from_stripe(obj)

        elif event_type in ("invoice.paid", "invoice.payment_failed"):
            stripe_subscription_id = obj.get("subscription")
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
