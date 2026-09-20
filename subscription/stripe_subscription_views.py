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
    if obj is None:
        return default
    if isinstance(obj, dict):
        return obj.get(key, default)
    try:
        return getattr(obj, key)
    except (AttributeError, KeyError, TypeError):
        return default


def _period_end_datetime(sub):
    value = _stripe_value(sub, "current_period_end")
    return datetime.fromtimestamp(value, tz=timezone.utc) if value else None


def _annual_line_items():
    price_id = getattr(settings, "STRIPE_SUBSCRIPTION_PRICE_ID", "")
    if price_id:
        return [{"price": price_id, "quantity": 1}]
    return [{"price_data": {"currency": "usd", "product_data": {"name": "PandaSpeak Annual Subscription", "description": "Annual access to PandaSpeak Chinese learning materials."}, "unit_amount": 1500, "recurring": {"interval": "year"}}, "quantity": 1}]


def _plus_price():
    return getattr(settings, "STRIPE_PLUS_PRICE_ID", "")


def _sync_base_from_stripe(remote, user=None, payment_confirmed=None):
    metadata = _stripe_value(remote, "metadata", {}) or {}
    if _stripe_value(metadata, "purpose") != "pandaspeak_annual_subscription":
        return
    sid = _stripe_value(remote, "id")
    if not sid:
        return
    if user is None:
        try:
            user = User.objects.get(pk=_stripe_value(metadata, "user_id"))
        except (User.DoesNotExist, ValueError, TypeError):
            return
    local, _ = Subscription.objects.get_or_create(user=user, defaults={"subscription_plan": "standard", "subscription_cost": 15.00})
    if local.stripe_subscription_id and local.stripe_subscription_id != sid:
        return
    status = _stripe_value(remote, "status")
    terminal = status in ("canceled", "unpaid", "incomplete_expired")
    cancel_end = bool(_stripe_value(remote, "cancel_at_period_end", False))
    local.subscription_plan = "standard"
    local.subscription_cost = 15.00
    local.stripe_subscription_id = sid
    if payment_confirmed is True:
        local.is_active = status in ("active", "trialing")
    elif payment_confirmed is False or terminal:
        local.is_active = False
    local.is_cancelled = cancel_end or terminal
    local.access_until = _period_end_datetime(remote)
    local.save()


def _sync_plus_from_stripe(remote, user=None, payment_confirmed=None):
    metadata = _stripe_value(remote, "metadata", {}) or {}
    if _stripe_value(metadata, "purpose") != "pandaspeak_plus_addon":
        return
    sid = _stripe_value(remote, "id")
    if not sid:
        return
    if user is None:
        try:
            user = User.objects.get(pk=_stripe_value(metadata, "user_id"))
        except (User.DoesNotExist, ValueError, TypeError):
            return
    local = Subscription.objects.filter(user=user).first()
    if not local or not local.is_active:
        return
    if local.plus_stripe_subscription_id and local.plus_stripe_subscription_id != sid:
        return
    status = _stripe_value(remote, "status")
    terminal = status in ("canceled", "unpaid", "incomplete_expired")
    cancel_end = bool(_stripe_value(remote, "cancel_at_period_end", False))
    local.plus_stripe_subscription_id = sid
    if payment_confirmed is True:
        local.plus_is_active = status in ("active", "trialing")
    elif payment_confirmed is False:
        local.plus_is_active = False
    elif terminal:
        local.plus_is_active = False
    local.plus_is_cancelled = cancel_end or terminal
    local.plus_access_until = _period_end_datetime(remote)
    local.save(update_fields=["plus_stripe_subscription_id", "plus_is_active", "plus_is_cancelled", "plus_access_until"])


@login_required
def stripe_subscription_checkout(request):
    if request.method != "POST":
        return redirect("subscribe")
    existing = Subscription.objects.filter(user=request.user).first()
    if existing and existing.is_active and not existing.is_cancelled:
        messages.info(request, "You already have an active PandaSpeak annual subscription. No additional payment was created.")
        return redirect("student_dashboard")
    try:
        session = stripe.checkout.Session.create(
            api_key=_subscription_api_key(), mode="subscription",
            payment_method_types=["card", "us_bank_account"],
            payment_method_options={"us_bank_account": {"verification_method": "automatic"}},
            customer_email=request.user.email or None, line_items=_annual_line_items(),
            success_url=request.build_absolute_uri("/subscription/stripe/success/") + "?session_id={CHECKOUT_SESSION_ID}",
            cancel_url=request.build_absolute_uri("/subscription/subscribe/"),
            metadata={"purpose": "pandaspeak_annual_subscription", "user_id": str(request.user.id)},
            subscription_data={"metadata": {"purpose": "pandaspeak_annual_subscription", "user_id": str(request.user.id)}},
        )
        return redirect(session.url)
    except stripe.error.StripeError:
        messages.error(request, "Unable to start Stripe checkout right now. Please try again.")
        return redirect("subscribe")


@login_required
def stripe_plus_upgrade(request):
    """Create a separate monthly Plus add-on; never replace the $15 annual membership."""
    if request.method != "POST":
        return redirect("plus_upgrade")
    local = Subscription.objects.filter(user=request.user).first()
    if not local or not local.is_active or local.is_cancelled:
        messages.error(request, "An active PandaSpeak Standard annual subscription is required before upgrading.")
        return redirect("subscribe")
    if local.plus_is_active:
        messages.info(request, "You already have PandaSpeak Plus.")
        return redirect("plus_upgrade")
    if not _plus_price():
        messages.error(request, "PandaSpeak Plus billing is not configured yet.")
        return redirect("plus_upgrade")
    try:
        session = stripe.checkout.Session.create(
            api_key=_subscription_api_key(), mode="subscription", payment_method_types=["card"],
            customer_email=request.user.email or None,
            line_items=[{"price": _plus_price(), "quantity": 1}],
            success_url=request.build_absolute_uri("/subscription/stripe/plus-success/") + "?session_id={CHECKOUT_SESSION_ID}",
            cancel_url=request.build_absolute_uri("/student/plus/"),
            metadata={"purpose": "pandaspeak_plus_addon", "user_id": str(request.user.id)},
            subscription_data={"metadata": {"purpose": "pandaspeak_plus_addon", "user_id": str(request.user.id)}},
        )
        return redirect(session.url)
    except stripe.error.StripeError:
        messages.error(request, "Unable to start PandaSpeak Plus checkout. Your annual subscription was not changed.")
        return redirect("plus_upgrade")


# Kept for compatibility with the route/button created during the earlier PayPal
# migration work. PayPal Standard now stays active; only Plus is purchased on Stripe.
@login_required
def stripe_plus_migration_checkout(request):
    return stripe_plus_upgrade(request)


@login_required
def stripe_plus_migration_success(request):
    return stripe_plus_success(request)


@login_required
def stripe_plus_success(request):
    session_id = request.GET.get("session_id", "")
    try:
        session = stripe.checkout.Session.retrieve(session_id, api_key=_subscription_api_key())
    except stripe.error.StripeError:
        messages.error(request, "We could not verify the Plus payment. Your annual subscription was not changed.")
        return redirect("plus_upgrade")
    metadata = _stripe_value(session, "metadata", {}) or {}
    sid = _stripe_value(session, "subscription")
    if (_stripe_value(session, "mode") != "subscription" or _stripe_value(metadata, "purpose") != "pandaspeak_plus_addon" or str(_stripe_value(metadata, "user_id")) != str(request.user.id) or not sid):
        messages.error(request, "We could not safely verify this PandaSpeak Plus checkout.")
        return redirect("plus_upgrade")
    try:
        remote = stripe.Subscription.retrieve(sid, api_key=_subscription_api_key())
        _sync_plus_from_stripe(remote, user=request.user, payment_confirmed=_stripe_value(session, "payment_status") == "paid")
    except stripe.error.StripeError:
        messages.error(request, "Plus payment was received but synchronization is still pending. Please do not purchase again.")
        return redirect("plus_upgrade")
    messages.success(request, "Welcome to PandaSpeak Plus! Your $15 annual PandaSpeak subscription remains active separately.")
    return redirect("plus_upgrade")


@login_required
def stripe_subscription_success(request):
    session_id = request.GET.get("session_id", "")
    try:
        session = stripe.checkout.Session.retrieve(session_id, api_key=_subscription_api_key())
    except stripe.error.StripeError:
        messages.error(request, "We could not verify your Stripe subscription. Please contact PandaSpeak support if you were charged.")
        return redirect("subscribe")
    metadata = _stripe_value(session, "metadata", {}) or {}
    sid = _stripe_value(session, "subscription")
    if (_stripe_value(session, "mode") != "subscription" or _stripe_value(metadata, "purpose") != "pandaspeak_annual_subscription" or str(_stripe_value(metadata, "user_id")) != str(request.user.id) or not sid):
        messages.error(request, "We could not verify your Stripe subscription.")
        return redirect("subscribe")
    status = _stripe_value(session, "payment_status")
    try:
        _sync_base_from_stripe(stripe.Subscription.retrieve(sid, api_key=_subscription_api_key()), user=request.user, payment_confirmed=(status == "paid") if status in ("paid", "unpaid") else None)
    except stripe.error.StripeError:
        return render(request, "subscription/ach_pending.html", {"user": request.user})
    local = Subscription.objects.filter(user=request.user).first()
    if status != "paid" or not local or not local.is_active:
        return render(request, "subscription/ach_pending.html", {"user": request.user})
    return render(request, "subscription/success.html", {"user": request.user, "first_name": request.user.first_name})


@csrf_exempt
def stripe_subscription_webhook(request):
    if request.method != "POST":
        return HttpResponse(status=405)
    secret = getattr(settings, "STRIPE_SUBSCRIPTION_WEBHOOK_SECRET", "")
    if not secret:
        return HttpResponse("Subscription webhook secret is not configured.", status=503)
    try:
        event = stripe.Webhook.construct_event(request.body, request.META.get("HTTP_STRIPE_SIGNATURE", ""), secret)
    except (ValueError, stripe.error.SignatureVerificationError):
        return HttpResponse(status=400)
    event_type = _stripe_value(event, "type")
    obj = _stripe_value(_stripe_value(event, "data", {}) or {}, "object", {}) or {}
    try:
        if event_type in ("checkout.session.completed", "checkout.session.async_payment_succeeded"):
            metadata = _stripe_value(obj, "metadata", {}) or {}
            sid = _stripe_value(obj, "subscription")
            if sid:
                try:
                    user = User.objects.get(pk=_stripe_value(metadata, "user_id"))
                except (User.DoesNotExist, ValueError, TypeError):
                    return HttpResponse(status=200)
                remote = stripe.Subscription.retrieve(sid, api_key=_subscription_api_key())
                confirmed = event_type == "checkout.session.async_payment_succeeded" or _stripe_value(obj, "payment_status") == "paid"
                if _stripe_value(metadata, "purpose") == "pandaspeak_plus_addon":
                    _sync_plus_from_stripe(remote, user=user, payment_confirmed=confirmed)
                elif _stripe_value(metadata, "purpose") == "pandaspeak_annual_subscription":
                    _sync_base_from_stripe(remote, user=user, payment_confirmed=confirmed)
        elif event_type in ("customer.subscription.created", "customer.subscription.updated", "customer.subscription.deleted"):
            purpose = _stripe_value(_stripe_value(obj, "metadata", {}) or {}, "purpose")
            if purpose == "pandaspeak_plus_addon":
                _sync_plus_from_stripe(obj)
            elif purpose == "pandaspeak_annual_subscription":
                _sync_base_from_stripe(obj)
        elif event_type in ("invoice.paid", "invoice.payment_failed"):
            sid = _stripe_value(obj, "subscription")
            if sid:
                remote = stripe.Subscription.retrieve(sid, api_key=_subscription_api_key())
                purpose = _stripe_value(_stripe_value(remote, "metadata", {}) or {}, "purpose")
                confirmed = event_type == "invoice.paid"
                if purpose == "pandaspeak_plus_addon":
                    _sync_plus_from_stripe(remote, payment_confirmed=confirmed)
                elif purpose == "pandaspeak_annual_subscription":
                    _sync_base_from_stripe(remote, payment_confirmed=confirmed)
    except stripe.error.StripeError:
        return HttpResponse(status=500)
    return HttpResponse(status=200)
