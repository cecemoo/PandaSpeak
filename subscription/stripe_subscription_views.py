from datetime import datetime, timezone

import requests
import stripe
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.views.decorators.csrf import csrf_exempt

from .models import Subscription
from .views import _paypal_access_token, _paypal_headers

User = get_user_model()


def _subscription_api_key():
    return getattr(settings, "STRIPE_SUBSCRIPTION_SECRET_KEY", "") or settings.STRIPE_SECRET_KEY


def _stripe_value(obj, key, default=None):
    if obj is None: return default
    if isinstance(obj, dict): return obj.get(key, default)
    try: return getattr(obj, key)
    except (AttributeError, KeyError, TypeError): return default


def _annual_line_items():
    price_id = getattr(settings, "STRIPE_SUBSCRIPTION_PRICE_ID", "")
    if price_id: return [{"price": price_id, "quantity": 1}]
    return [{"price_data":{"currency":"usd","product_data":{"name":"PandaSpeak Annual Subscription","description":"Annual access to PandaSpeak Chinese learning materials."},"unit_amount":1500,"recurring":{"interval":"year"}},"quantity":1}]


def _stripe_plan(stripe_subscription):
    plus_price=getattr(settings,"STRIPE_PLUS_PRICE_ID",""); standard_price=getattr(settings,"STRIPE_SUBSCRIPTION_PRICE_ID","")
    items=_stripe_value(_stripe_value(stripe_subscription,"items",{}),"data",[]) or []; price_ids=[]
    for item in items:
        pid=_stripe_value(_stripe_value(item,"price",{}) or {},"id")
        if pid: price_ids.append(pid)
    if plus_price and plus_price in price_ids: return "plus",4.99
    if standard_price and standard_price in price_ids: return "standard",15.00
    metadata=_stripe_value(stripe_subscription,"metadata",{}) or {}
    if _stripe_value(metadata,"pandaspeak_plan")=="plus": return "plus",4.99
    return "standard",15.00


@login_required
def stripe_subscription_checkout(request):
    if request.method!="POST": return redirect("subscribe")
    existing=Subscription.objects.filter(user=request.user).first()
    if existing and existing.is_active and not existing.is_cancelled:
        messages.info(request,"You already have an active PandaSpeak subscription. No additional payment was created."); return redirect("student_dashboard")
    if not _subscription_api_key(): messages.error(request,"Stripe subscription checkout is not configured yet."); return redirect("subscribe")
    try:
        session=stripe.checkout.Session.create(api_key=_subscription_api_key(),mode="subscription",payment_method_types=["card","us_bank_account"],payment_method_options={"us_bank_account":{"verification_method":"automatic"}},customer_email=request.user.email or None,line_items=_annual_line_items(),success_url=request.build_absolute_uri("/subscription/stripe/success/")+"?session_id={CHECKOUT_SESSION_ID}",cancel_url=request.build_absolute_uri("/subscription/subscribe/"),metadata={"purpose":"pandaspeak_annual_subscription","user_id":str(request.user.id)},subscription_data={"metadata":{"purpose":"pandaspeak_annual_subscription","user_id":str(request.user.id),"pandaspeak_plan":"standard"},"payment_settings":{"payment_method_types":["card","us_bank_account"],"save_default_payment_method":"on_subscription"}})
        return redirect(session.url)
    except stripe.error.StripeError:
        messages.error(request,"Unable to start Stripe checkout right now. Please try again."); return redirect("subscribe")


def _period_end_datetime(sub):
    value=_stripe_value(sub,"current_period_end"); return datetime.fromtimestamp(value,tz=timezone.utc) if value else None


def _sync_subscription_from_stripe(stripe_subscription,user=None,payment_confirmed=None,preserve_paypal_id=None):
    metadata=_stripe_value(stripe_subscription,"metadata",{}) or {}
    if _stripe_value(metadata,"purpose")!="pandaspeak_annual_subscription": return
    sid=_stripe_value(stripe_subscription,"id")
    if not sid: return
    status=_stripe_value(stripe_subscription,"status"); cancel_end=bool(_stripe_value(stripe_subscription,"cancel_at_period_end",False))
    local=Subscription.objects.filter(stripe_subscription_id=sid).first()
    if local is None:
        if user is None:
            uid=_stripe_value(metadata,"user_id")
            if not uid: return
            try: user=User.objects.get(pk=uid)
            except (User.DoesNotExist,ValueError,TypeError): return
        local=Subscription.objects.filter(user=user).first()
        if local is None: local=Subscription.objects.create(user=user,subscription_plan="standard",subscription_cost=15.00)
        elif local.stripe_subscription_id and local.stripe_subscription_id!=sid and local.is_active and not local.is_cancelled: return
    plan,cost=_stripe_plan(stripe_subscription); local.subscription_plan=plan; local.subscription_cost=cost
    local.paypal_subscription_id=preserve_paypal_id
    local.stripe_subscription_id=sid
    terminal=status in ("canceled","unpaid","incomplete_expired")
    if payment_confirmed is True: local.is_active=status in ("active","trialing")
    elif payment_confirmed is False: local.is_active=False
    elif terminal: local.is_active=False
    local.is_cancelled=cancel_end or terminal; local.access_until=_period_end_datetime(stripe_subscription); local.save()


def _cancel_paypal_subscription(paypal_id):
    token=_paypal_access_token()
    if not token or not paypal_id: return False
    try:
        response=requests.post(f"{settings.PAYPAL_BASE_URL}/v1/billing/subscriptions/{paypal_id}/cancel",headers=_paypal_headers(token),json={"reason":"Customer upgraded to PandaSpeak Plus through Stripe."},timeout=20)
    except requests.RequestException: return False
    return response.status_code in (200,204,422)  # 422 can mean it is already non-cancellable/non-active.


@login_required
def stripe_plus_upgrade(request):
    if request.method!="POST": return redirect("plus_upgrade")
    local=Subscription.objects.filter(user=request.user).first()
    if not local or not local.is_active or local.is_cancelled: messages.error(request,"An active PandaSpeak Standard subscription is required before upgrading."); return redirect("subscribe")
    if str(local.subscription_plan).lower()=="plus": messages.info(request,"You already have PandaSpeak Plus."); return redirect("plus_upgrade")
    if not local.stripe_subscription_id: return redirect("stripe_plus_migration_checkout")
    plus_price=getattr(settings,"STRIPE_PLUS_PRICE_ID","")
    if not plus_price: messages.error(request,"PandaSpeak Plus billing is not configured yet."); return redirect("plus_upgrade")
    try:
        current=stripe.Subscription.retrieve(local.stripe_subscription_id,api_key=_subscription_api_key()); items=_stripe_value(_stripe_value(current,"items",{}),"data",[]) or []
        if len(items)!=1: messages.error(request,"We could not safely verify your current Stripe plan. No billing changes were made."); return redirect("plus_upgrade")
        metadata=dict(_stripe_value(current,"metadata",{}) or {})
        if metadata.get("purpose")!="pandaspeak_annual_subscription" or str(metadata.get("user_id"))!=str(request.user.id): messages.error(request,"We could not safely verify your current Stripe subscription. No billing changes were made."); return redirect("plus_upgrade")
        metadata["pandaspeak_plan"]="plus"
        updated=stripe.Subscription.modify(local.stripe_subscription_id,api_key=_subscription_api_key(),items=[{"id":_stripe_value(items[0],"id"),"price":plus_price}],metadata=metadata,proration_behavior="create_prorations")
        _sync_subscription_from_stripe(updated,user=request.user); local.refresh_from_db()
        if str(local.subscription_plan).lower()!="plus": messages.error(request,"Stripe was updated, but PandaSpeak could not confirm Plus access yet. Please contact support before retrying."); return redirect("plus_upgrade")
        messages.success(request,"Welcome to PandaSpeak Plus! Your Stripe subscription and PandaSpeak account are synchronized."); return redirect("plus_upgrade")
    except stripe.error.StripeError:
        messages.error(request,"Stripe could not complete the Plus upgrade. Your PandaSpeak access was not changed."); return redirect("plus_upgrade")


@login_required
def stripe_plus_migration_checkout(request):
    """Move an active PayPal Standard subscriber to a new Stripe Plus subscription."""
    local=Subscription.objects.filter(user=request.user).first()
    if not local or not local.is_active or local.is_cancelled or not local.paypal_subscription_id or local.stripe_subscription_id:
        messages.error(request,"A verified active PayPal Standard subscription is required for this upgrade path."); return redirect("plus_upgrade")
    if request.method!="POST": return redirect("plus_upgrade")
    if request.POST.get("accept_nonrefundable")!="yes":
        messages.error(request,"Please acknowledge the annual Standard subscription policy before upgrading."); return redirect("plus_upgrade")
    plus_price=getattr(settings,"STRIPE_PLUS_PRICE_ID","")
    if not plus_price: messages.error(request,"PandaSpeak Plus billing is not configured yet."); return redirect("plus_upgrade")
    try:
        session=stripe.checkout.Session.create(api_key=_subscription_api_key(),mode="subscription",payment_method_types=["card"],customer_email=request.user.email or None,line_items=[{"price":plus_price,"quantity":1}],success_url=request.build_absolute_uri("/subscription/stripe/plus-migration-success/")+"?session_id={CHECKOUT_SESSION_ID}",cancel_url=request.build_absolute_uri("/student/plus/"),metadata={"purpose":"pandaspeak_plus_migration","user_id":str(request.user.id),"paypal_subscription_id":local.paypal_subscription_id},subscription_data={"metadata":{"purpose":"pandaspeak_annual_subscription","user_id":str(request.user.id),"pandaspeak_plan":"plus","migration_from_paypal":local.paypal_subscription_id}})
        return redirect(session.url)
    except stripe.error.StripeError:
        messages.error(request,"Unable to start the PandaSpeak Plus checkout. Your PayPal subscription was not changed."); return redirect("plus_upgrade")


@login_required
def stripe_plus_migration_success(request):
    session_id=request.GET.get("session_id","")
    try: session=stripe.checkout.Session.retrieve(session_id,api_key=_subscription_api_key())
    except stripe.error.StripeError: messages.error(request,"We could not verify the Plus payment. Your PayPal subscription remains unchanged."); return redirect("plus_upgrade")
    metadata=_stripe_value(session,"metadata",{}) or {}; sid=_stripe_value(session,"subscription"); paypal_id=_stripe_value(metadata,"paypal_subscription_id")
    if _stripe_value(session,"mode")!="subscription" or _stripe_value(metadata,"purpose")!="pandaspeak_plus_migration" or str(_stripe_value(metadata,"user_id"))!=str(request.user.id) or _stripe_value(session,"payment_status")!="paid" or not sid or not paypal_id:
        messages.error(request,"Plus payment is not confirmed yet. Your PayPal subscription remains unchanged."); return redirect("plus_upgrade")
    local=Subscription.objects.filter(user=request.user).first()
    if not local or local.paypal_subscription_id!=paypal_id:
        messages.error(request,"We could not safely match the PayPal subscription. Please contact support before retrying."); return redirect("plus_upgrade")
    try: stripe_sub=stripe.Subscription.retrieve(sid,api_key=_subscription_api_key())
    except stripe.error.StripeError: messages.error(request,"Stripe payment succeeded but PandaSpeak could not finish synchronization. Please contact support; do not retry payment."); return redirect("plus_upgrade")
    # Keep the PayPal ID in Django until cancellation succeeds, so a failed cancellation is recoverable.
    _sync_subscription_from_stripe(stripe_sub,user=request.user,payment_confirmed=True,preserve_paypal_id=paypal_id)
    if not _cancel_paypal_subscription(paypal_id):
        messages.error(request,"Your Plus payment succeeded, but PandaSpeak could not confirm cancellation of the old PayPal renewal. Please contact support; do not purchase Plus again."); return redirect("plus_upgrade")
    local.refresh_from_db(); local.paypal_subscription_id=None; local.subscription_plan="plus"; local.subscription_cost=4.99; local.is_active=True; local.is_cancelled=False; local.save()
    messages.success(request,"Welcome to PandaSpeak Plus! Stripe is now your billing provider and your old PayPal renewal has been cancelled. The $15 annual Standard subscription remains nonrefundable."); return redirect("plus_upgrade")


@login_required
def stripe_subscription_success(request):
    session_id=request.GET.get("session_id","")
    if not session_id: messages.error(request,"Stripe did not return a checkout session ID."); return redirect("subscribe")
    try: session=stripe.checkout.Session.retrieve(session_id,api_key=_subscription_api_key())
    except stripe.error.StripeError: messages.error(request,"We could not verify your Stripe subscription. Please contact PandaSpeak support if you were charged."); return redirect("subscribe")
    metadata=_stripe_value(session,"metadata",{}) or {}; sid=_stripe_value(session,"subscription")
    if _stripe_value(session,"mode")!="subscription" or _stripe_value(metadata,"purpose")!="pandaspeak_annual_subscription" or str(_stripe_value(metadata,"user_id"))!=str(request.user.id) or not sid: messages.error(request,"We could not verify your Stripe subscription. Please contact PandaSpeak support if you were charged."); return redirect("subscribe")
    status=_stripe_value(session,"payment_status")
    try: _sync_subscription_from_stripe(stripe.Subscription.retrieve(sid,api_key=_subscription_api_key()),user=request.user,payment_confirmed=(status=="paid") if status in ("paid","unpaid") else None)
    except stripe.error.StripeError: return render(request,"subscription/ach_pending.html",{"user":request.user})
    local=Subscription.objects.filter(user=request.user).first()
    if status!="paid" or not local or not local.is_active: return render(request,"subscription/ach_pending.html",{"user":request.user})
    return render(request,"subscription/success.html",{"user":request.user,"first_name":request.user.first_name})


@csrf_exempt
def stripe_subscription_webhook(request):
    if request.method!="POST": return HttpResponse(status=405)
    secret=getattr(settings,"STRIPE_SUBSCRIPTION_WEBHOOK_SECRET","")
    if not secret: return HttpResponse("Subscription webhook secret is not configured.",status=503)
    try: event=stripe.Webhook.construct_event(request.body,request.META.get("HTTP_STRIPE_SIGNATURE",""),secret)
    except (ValueError,stripe.error.SignatureVerificationError): return HttpResponse(status=400)
    et=_stripe_value(event,"type"); obj=_stripe_value(_stripe_value(event,"data",{}) or {},"object",{}) or {}
    try:
        if et in ("checkout.session.completed","checkout.session.async_payment_succeeded"):
            metadata=_stripe_value(obj,"metadata",{}) or {}; sid=_stripe_value(obj,"subscription")
            # Standard checkout only. PayPal migration is finalized by its verified success endpoint so the PayPal ID is retained until cancellation.
            if _stripe_value(obj,"mode")=="subscription" and _stripe_value(metadata,"purpose")=="pandaspeak_annual_subscription" and sid:
                try: user=User.objects.get(pk=_stripe_value(metadata,"user_id"))
                except (User.DoesNotExist,ValueError,TypeError): return HttpResponse(status=200)
                sub=stripe.Subscription.retrieve(sid,api_key=_subscription_api_key()); confirmed=et=="checkout.session.async_payment_succeeded" or _stripe_value(obj,"payment_status")=="paid"; _sync_subscription_from_stripe(sub,user=user,payment_confirmed=confirmed)
        elif et=="checkout.session.async_payment_failed":
            sid=_stripe_value(obj,"subscription")
            if sid: _sync_subscription_from_stripe(stripe.Subscription.retrieve(sid,api_key=_subscription_api_key()),payment_confirmed=False)
        elif et in ("customer.subscription.created","customer.subscription.updated","customer.subscription.deleted"):
            # During PayPal migration, do not erase the old PayPal ID before the success endpoint cancels it.
            metadata=_stripe_value(obj,"metadata",{}) or {}; old_paypal=_stripe_value(metadata,"migration_from_paypal")
            _sync_subscription_from_stripe(obj,preserve_paypal_id=old_paypal)
        elif et in ("invoice.paid","invoice.payment_failed"):
            sid=_stripe_value(obj,"subscription")
            if sid:
                sub=stripe.Subscription.retrieve(sid,api_key=_subscription_api_key()); metadata=_stripe_value(sub,"metadata",{}) or {}; _sync_subscription_from_stripe(sub,payment_confirmed=(et=="invoice.paid"),preserve_paypal_id=_stripe_value(metadata,"migration_from_paypal"))
    except stripe.error.StripeError: return HttpResponse(status=500)
    return HttpResponse(status=200)
