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


def _annual_line_items():
    price_id = getattr(settings, "STRIPE_SUBSCRIPTION_PRICE_ID", "")
    if price_id:
        return [{"price": price_id, "quantity": 1}]
    return [{"price_data":{"currency":"usd","product_data":{"name":"PandaSpeak Annual Subscription","description":"Annual access to PandaSpeak Chinese learning materials."},"unit_amount":1500,"recurring":{"interval":"year"}},"quantity":1}]


def _stripe_plan(stripe_subscription):
    """Determine the billing plan from the actual Stripe subscription price."""
    plus_price = getattr(settings, "STRIPE_PLUS_PRICE_ID", "")
    standard_price = getattr(settings, "STRIPE_SUBSCRIPTION_PRICE_ID", "")
    items = _stripe_value(_stripe_value(stripe_subscription, "items", {}), "data", []) or []
    price_ids = []
    for item in items:
        price = _stripe_value(item, "price", {}) or {}
        price_id = _stripe_value(price, "id")
        if price_id:
            price_ids.append(price_id)
    if plus_price and plus_price in price_ids:
        return "plus", 4.99
    if standard_price and standard_price in price_ids:
        return "standard", 15.00
    metadata = _stripe_value(stripe_subscription, "metadata", {}) or {}
    if _stripe_value(metadata, "pandaspeak_plan") == "plus":
        return "plus", 4.99
    return "standard", 15.00


@login_required
def stripe_subscription_checkout(request):
    if request.method != "POST":
        return redirect("subscribe")
    existing = Subscription.objects.filter(user=request.user).first()
    if existing and existing.is_active and not existing.is_cancelled:
        messages.info(request, "You already have an active PandaSpeak subscription. No additional payment was created.")
        return redirect("student_dashboard")
    api_key = _subscription_api_key()
    if not api_key:
        messages.error(request, "Stripe subscription checkout is not configured yet.")
        return redirect("subscribe")
    try:
        checkout_session = stripe.checkout.Session.create(
            api_key=api_key, mode="subscription", payment_method_types=["card","us_bank_account"],
            payment_method_options={"us_bank_account":{"verification_method":"automatic"}}, customer_email=request.user.email or None,
            line_items=_annual_line_items(), success_url=request.build_absolute_uri("/subscription/stripe/success/")+"?session_id={CHECKOUT_SESSION_ID}",
            cancel_url=request.build_absolute_uri("/subscription/subscribe/"), metadata={"purpose":"pandaspeak_annual_subscription","user_id":str(request.user.id)},
            subscription_data={"metadata":{"purpose":"pandaspeak_annual_subscription","user_id":str(request.user.id),"pandaspeak_plan":"standard"},"payment_settings":{"payment_method_types":["card","us_bank_account"],"save_default_payment_method":"on_subscription"}},
        )
        return redirect(checkout_session.url)
    except stripe.error.StripeError:
        messages.error(request, "Unable to start Stripe checkout right now. Please try again.")
        return redirect("subscribe")


def _period_end_datetime(stripe_subscription):
    period_end = _stripe_value(stripe_subscription, "current_period_end")
    return datetime.fromtimestamp(period_end, tz=timezone.utc) if period_end else None


def _sync_subscription_from_stripe(stripe_subscription, user=None, payment_confirmed=None):
    metadata = _stripe_value(stripe_subscription, "metadata", {}) or {}
    if _stripe_value(metadata, "purpose") != "pandaspeak_annual_subscription":
        return
    stripe_subscription_id = _stripe_value(stripe_subscription, "id")
    if not stripe_subscription_id:
        return
    status = _stripe_value(stripe_subscription, "status")
    cancel_at_period_end = bool(_stripe_value(stripe_subscription, "cancel_at_period_end", False))
    local_subscription = Subscription.objects.filter(stripe_subscription_id=stripe_subscription_id).first()
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
            if existing.stripe_subscription_id and existing.stripe_subscription_id != stripe_subscription_id and existing.is_active and not existing.is_cancelled:
                return
            local_subscription = existing
        else:
            local_subscription = Subscription.objects.create(user=user, subscription_plan="standard", subscription_cost=15.00)

    plan, cost = _stripe_plan(stripe_subscription)
    local_subscription.subscription_plan = plan
    local_subscription.subscription_cost = cost
    local_subscription.paypal_subscription_id = None
    local_subscription.stripe_subscription_id = stripe_subscription_id
    terminal = status in ("canceled","unpaid","incomplete_expired")
    if payment_confirmed is True:
        local_subscription.is_active = status in ("active","trialing")
    elif payment_confirmed is False:
        local_subscription.is_active = False
    elif terminal:
        local_subscription.is_active = False
    local_subscription.is_cancelled = cancel_at_period_end or terminal
    local_subscription.access_until = _period_end_datetime(stripe_subscription)
    local_subscription.save()


@login_required
def stripe_plus_upgrade(request):
    """Upgrade one existing Stripe Standard subscription to Plus; never create a second subscription."""
    if request.method != "POST":
        return redirect("plus_upgrade")
    local = Subscription.objects.filter(user=request.user).first()
    if not local or not local.is_active or local.is_cancelled:
        messages.error(request, "An active PandaSpeak Standard subscription is required before upgrading.")
        return redirect("subscribe")
    if str(local.subscription_plan).lower() == "plus":
        messages.info(request, "You already have PandaSpeak Plus.")
        return redirect("plus_upgrade")
    if not local.stripe_subscription_id:
        messages.info(request, "Your current subscription was not created through Stripe. Please contact PandaSpeak support before changing to Plus.")
        return redirect("plus_upgrade")
    plus_price = getattr(settings, "STRIPE_PLUS_PRICE_ID", "")
    if not plus_price:
        messages.error(request, "PandaSpeak Plus billing is not configured yet.")
        return redirect("plus_upgrade")
    try:
        current = stripe.Subscription.retrieve(local.stripe_subscription_id, api_key=_subscription_api_key())
        items = _stripe_value(_stripe_value(current, "items", {}), "data", []) or []
        if len(items) != 1:
            messages.error(request, "We could not safely verify your current Stripe plan. No billing changes were made.")
            return redirect("plus_upgrade")
        item_id = _stripe_value(items[0], "id")
        metadata = dict(_stripe_value(current, "metadata", {}) or {})
        if metadata.get("purpose") != "pandaspeak_annual_subscription" or str(metadata.get("user_id")) != str(request.user.id):
            messages.error(request, "We could not safely verify your current Stripe subscription. No billing changes were made.")
            return redirect("plus_upgrade")
        metadata["pandaspeak_plan"] = "plus"
        updated = stripe.Subscription.modify(
            local.stripe_subscription_id,
            api_key=_subscription_api_key(),
            items=[{"id":item_id,"price":plus_price}],
            metadata=metadata,
            proration_behavior="create_prorations",
        )
        # Synchronize Django immediately from Stripe's returned source of truth.
        _sync_subscription_from_stripe(updated, user=request.user)
        local.refresh_from_db()
        if str(local.subscription_plan).lower() != "plus":
            messages.error(request, "Stripe was updated, but PandaSpeak could not confirm Plus access yet. Please contact support before retrying.")
            return redirect("plus_upgrade")
        messages.success(request, "Welcome to PandaSpeak Plus! Your Stripe subscription and PandaSpeak account are synchronized.")
        return redirect("plus_upgrade")
    except stripe.error.StripeError:
        messages.error(request, "Stripe could not complete the Plus upgrade. Your PandaSpeak access was not changed.")
        return redirect("plus_upgrade")


@login_required
def stripe_subscription_success(request):
    session_id = request.GET.get("session_id", "")
    if not session_id:
        messages.error(request, "Stripe did not return a checkout session ID.")
        return redirect("subscribe")
    try:
        checkout_session = stripe.checkout.Session.retrieve(session_id, api_key=_subscription_api_key())
    except stripe.error.StripeError:
        messages.error(request, "We could not verify your Stripe subscription. Please contact PandaSpeak support if you were charged.")
        return redirect("subscribe")
    metadata = _stripe_value(checkout_session, "metadata", {}) or {}
    subscription_id = _stripe_value(checkout_session, "subscription")
    if (_stripe_value(checkout_session,"mode")!="subscription" or _stripe_value(metadata,"purpose")!="pandaspeak_annual_subscription" or str(_stripe_value(metadata,"user_id"))!=str(request.user.id) or not subscription_id):
        messages.error(request, "We could not verify your Stripe subscription. Please contact PandaSpeak support if you were charged.")
        return redirect("subscribe")
    payment_status = _stripe_value(checkout_session, "payment_status")
    try:
        stripe_subscription = stripe.Subscription.retrieve(subscription_id, api_key=_subscription_api_key())
        _sync_subscription_from_stripe(stripe_subscription,user=request.user,payment_confirmed=(payment_status=="paid") if payment_status in ("paid","unpaid") else None)
    except stripe.error.StripeError:
        return render(request,"subscription/ach_pending.html",{"user":request.user})
    local_subscription = Subscription.objects.filter(user=request.user).first()
    if payment_status != "paid" or not local_subscription or not local_subscription.is_active:
        return render(request,"subscription/ach_pending.html",{"user":request.user})
    return render(request,"subscription/success.html",{"user":request.user,"first_name":request.user.first_name})


@csrf_exempt
def stripe_subscription_webhook(request):
    if request.method != "POST": return HttpResponse(status=405)
    webhook_secret = getattr(settings,"STRIPE_SUBSCRIPTION_WEBHOOK_SECRET","")
    if not webhook_secret: return HttpResponse("Subscription webhook secret is not configured.",status=503)
    try:
        event = stripe.Webhook.construct_event(request.body,request.META.get("HTTP_STRIPE_SIGNATURE",""),webhook_secret)
    except (ValueError,stripe.error.SignatureVerificationError): return HttpResponse(status=400)
    event_type = _stripe_value(event,"type")
    obj = _stripe_value(_stripe_value(event,"data",{}) or {},"object",{}) or {}
    try:
        if event_type in ("checkout.session.completed","checkout.session.async_payment_succeeded"):
            metadata=_stripe_value(obj,"metadata",{}) or {}; subscription_id=_stripe_value(obj,"subscription")
            if _stripe_value(obj,"mode")=="subscription" and _stripe_value(metadata,"purpose")=="pandaspeak_annual_subscription" and subscription_id:
                try: user=User.objects.get(pk=_stripe_value(metadata,"user_id"))
                except (User.DoesNotExist,ValueError,TypeError): return HttpResponse(status=200)
                sub=stripe.Subscription.retrieve(subscription_id,api_key=_subscription_api_key())
                confirmed=event_type=="checkout.session.async_payment_succeeded" or _stripe_value(obj,"payment_status")=="paid"
                _sync_subscription_from_stripe(sub,user=user,payment_confirmed=confirmed)
        elif event_type=="checkout.session.async_payment_failed":
            sid=_stripe_value(obj,"subscription")
            if sid: _sync_subscription_from_stripe(stripe.Subscription.retrieve(sid,api_key=_subscription_api_key()),payment_confirmed=False)
        elif event_type in ("customer.subscription.created","customer.subscription.updated","customer.subscription.deleted"):
            _sync_subscription_from_stripe(obj)
        elif event_type in ("invoice.paid","invoice.payment_failed"):
            sid=_stripe_value(obj,"subscription")
            if sid: _sync_subscription_from_stripe(stripe.Subscription.retrieve(sid,api_key=_subscription_api_key()),payment_confirmed=(event_type=="invoice.paid"))
    except stripe.error.StripeError: return HttpResponse(status=500)
    return HttpResponse(status=200)
