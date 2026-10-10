from datetime import datetime, timezone

import stripe
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.db import transaction
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.utils import timezone as django_timezone
from django.views.decorators.csrf import csrf_exempt

from account.models import Notification
from .checkout_consent import require_checkout_consent
from .models import Subscription
from .referrals import available_reward_count, consume_paid_plus_reward

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
    if local.is_disputed:
        local.is_active = False
        local.plus_is_active = False
    elif payment_confirmed is True:
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
    if not local or not local.is_active or local.is_disputed:
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


def _stripe_subscription_from_dispute(dispute):
    """Return the PandaSpeak annual Stripe subscription related to a dispute."""
    charge_id = _stripe_value(dispute, "charge")
    if not charge_id:
        return None, None
    charge = stripe.Charge.retrieve(charge_id, api_key=_subscription_api_key())
    invoice_id = _stripe_value(charge, "invoice")
    if invoice_id:
        invoice = stripe.Invoice.retrieve(invoice_id, api_key=_subscription_api_key())
        sid = _stripe_value(invoice, "subscription")
        if sid:
            remote = stripe.Subscription.retrieve(sid, api_key=_subscription_api_key())
            return remote, charge_id
    payment_intent_id = _stripe_value(charge, "payment_intent")
    if not payment_intent_id:
        return None, charge_id
    sessions = stripe.checkout.Session.list(payment_intent=payment_intent_id, limit=10, api_key=_subscription_api_key())
    for session in sessions.auto_paging_iter():
        metadata = _stripe_value(session, "metadata", {}) or {}
        purpose = _stripe_value(metadata, "purpose")
        if purpose and purpose != "pandaspeak_annual_subscription":
            continue
        sid = _stripe_value(session, "subscription")
        if not sid:
            continue
        remote = stripe.Subscription.retrieve(sid, api_key=_subscription_api_key())
        return remote, charge_id
    return None, charge_id


def _record_subscription_dispute(dispute):
    """Block only a student who had active annual learning access when disputed."""
    remote, charge_id = _stripe_subscription_from_dispute(dispute)
    if remote is None:
        return
    sid = _stripe_value(remote, "id")
    local = Subscription.objects.filter(stripe_subscription_id=sid).first()
    if not local or (local.dispute_external_id and local.dispute_external_id != _stripe_value(dispute, "id")):
        return
    if local.dispute_status == "lost":
        return  # A late or repeated event must never undo a final loss.
    local.is_disputed = True
    local.dispute_status = _stripe_value(dispute, "status", "open") or "open"
    local.dispute_provider = "stripe"
    local.dispute_external_id = _stripe_value(dispute, "id", "") or ""
    local.dispute_charge_id = charge_id or ""
    local.disputed_at = django_timezone.now()
    local.is_active = False
    local.plus_is_active = False
    local.save(update_fields=["is_disputed", "dispute_status", "dispute_provider", "dispute_external_id", "dispute_charge_id", "disputed_at", "is_active", "plus_is_active"])


def _send_dispute_resolution_email(local, restored):
    student = local.user
    if not student.email:
        return
    greeting_name = student.first_name or student.get_full_name() or "Student"
    if restored:
        subject = "PandaSpeak Access Restored - Payment Dispute Resolved"
        message = (f"Dear {greeting_name},\n\n" "We received confirmation through Stripe that the payment dispute associated with your PandaSpeak annual subscription has been resolved in PandaSpeak's favor. " "Your PandaSpeak learning-material access has been restored for the remainder of your current eligible subscription period.\n\n" "You may sign in and continue using PandaSpeak normally.\n\n" "Best,\n" "PandaSpeak Team")
    else:
        subject = "PandaSpeak Payment Dispute Resolved"
        message = (f"Dear {greeting_name},\n\n" "We received the final outcome of the payment dispute associated with your PandaSpeak annual subscription. " "The dispute was resolved in the cardholder's favor, so your PandaSpeak paid learning-material access remains suspended.\n\n" "If you believe this status is incorrect, please contact your bank or card issuer and PandaSpeak Support at pandaspeaksupport@gmail.com.\n\n" "Best,\n" "PandaSpeak Team")
    send_mail(subject=subject, message=message, from_email=settings.DEFAULT_FROM_EMAIL, recipient_list=[student.email], fail_silently=True)


def _send_dispute_resolution_notification(local, restored):
    if restored:
        Notification.objects.create(
            user=local.user,
            title="PandaSpeak Access Restored - Payment Dispute Resolved",
            message=(
                "Stripe has confirmed that the payment dispute associated with your PandaSpeak annual subscription "
                "was resolved in PandaSpeak's favor. Your eligible learning-material and activity access has been restored. "
                "You may continue using PandaSpeak normally."
            ),
            link="/student/dashboard/",
        )
    else:
        Notification.objects.create(
            user=local.user,
            title="PandaSpeak Payment Dispute Resolved",
            message=(
                "Stripe has confirmed the final outcome of the payment dispute associated with your PandaSpeak annual subscription. "
                "The dispute was resolved in the cardholder's favor, so your paid learning-material and activity access remains suspended."
            ),
            link="/subscription/dispute-restricted/",
        )


def _update_subscription_dispute_status(dispute):
    dispute_id = _stripe_value(dispute, "id", "") or ""
    status = _stripe_value(dispute, "status", "") or ""
    if not dispute_id:
        return
    local = Subscription.objects.select_related("user").filter(dispute_provider="stripe", dispute_external_id=dispute_id).first()
    if not local:
        _record_subscription_dispute(dispute)
        local = Subscription.objects.select_related("user").filter(dispute_provider="stripe", dispute_external_id=dispute_id).first()
        if not local:
            return
    if local.dispute_status == "lost" and status != "lost":
        return
    previous_status = local.dispute_status
    final_favorable = status in ("won", "warning_closed")
    final_lost = status == "lost"
    if final_favorable:
        remote = stripe.Subscription.retrieve(local.stripe_subscription_id, api_key=_subscription_api_key())
        remote_status = _stripe_value(remote, "status", "")
        access_until = _period_end_datetime(remote) or local.access_until
        still_in_paid_period = not access_until or access_until > django_timezone.now()
        restore_access = remote_status in ("active", "trialing") and still_in_paid_period
        Subscription.objects.filter(pk=local.pk).update(dispute_status=status, is_disputed=False, is_active=restore_access, access_until=access_until)
        if previous_status != status:
            local.dispute_status = status
            local.is_disputed = False
            local.is_active = restore_access
            local.access_until = access_until
            _send_dispute_resolution_email(local, restored=restore_access)
            _send_dispute_resolution_notification(local, restored=restore_access)
        return
    if final_lost:
        Subscription.objects.filter(pk=local.pk).update(dispute_status=status, is_disputed=True, is_active=False, plus_is_active=False)
        if previous_status != status:
            local.dispute_status = status
            local.is_disputed = True
            local.is_active = False
            _send_dispute_resolution_email(local, restored=False)
            _send_dispute_resolution_notification(local, restored=False)
        return
    Subscription.objects.filter(pk=local.pk).update(dispute_status=status)


def _apply_reward_to_upcoming_plus_invoice(invoice):
    sid = _stripe_value(invoice, "subscription")
    if not sid or _stripe_value(invoice, "billing_reason") != "subscription_cycle":
        return
    remote = stripe.Subscription.retrieve(sid, api_key=_subscription_api_key())
    metadata = _stripe_value(remote, "metadata", {}) or {}
    if _stripe_value(metadata, "purpose") != "pandaspeak_plus_addon":
        return
    try:
        user = User.objects.get(pk=_stripe_value(metadata, "user_id"))
    except (User.DoesNotExist, ValueError, TypeError):
        return
    if not available_reward_count(user):
        return
    invoice_metadata = _stripe_value(invoice, "metadata", {}) or {}
    if _stripe_value(invoice_metadata, "pandaspeak_referral_reward") == "1":
        return
    coupon = stripe.Coupon.create(api_key=_subscription_api_key(), percent_off=100, duration="once", name="PandaSpeak Referral - Free Plus Month")
    stripe.Invoice.modify(_stripe_value(invoice, "id"), api_key=_subscription_api_key(), discounts=[{"coupon": coupon.id}], metadata={**dict(invoice_metadata), "pandaspeak_referral_reward": "1", "pandaspeak_reward_user_id": str(user.pk)})


def _consume_reward_from_paid_invoice(invoice):
    metadata = _stripe_value(invoice, "metadata", {}) or {}
    if _stripe_value(metadata, "pandaspeak_referral_reward") != "1" or (_stripe_value(invoice, "amount_due", 0) or 0) != 0:
        return
    try:
        user = User.objects.get(pk=_stripe_value(metadata, "pandaspeak_reward_user_id"))
    except (User.DoesNotExist, ValueError, TypeError):
        return
    consume_paid_plus_reward(user)


@login_required
def stripe_subscription_checkout(request):
    if request.method != "POST":
        return redirect("subscribe")
    consent_response = require_checkout_consent(request)
    if consent_response is not None:
        return consent_response
    # Serialize checkout creation per user in PostgreSQL, including first-time users.
    # A database row persists across workers and application restarts.
    try:
        with transaction.atomic():
            User.objects.select_for_update().get(pk=request.user.pk)
            existing, _ = Subscription.objects.get_or_create(
                user=request.user,
                defaults={"subscription_plan": "standard", "subscription_cost": 15.00},
            )
            if existing.is_disputed:
                messages.error(request, "This account cannot purchase learning access while a payment dispute is recorded.")
                return redirect("dispute_restricted")
            if existing.is_active:
                messages.info(request, "You already have an active PandaSpeak subscription. No additional payment was created.")
                return redirect("student_dashboard")
            if existing.pending_stripe_checkout_id:
                pending = stripe.checkout.Session.retrieve(
                    existing.pending_stripe_checkout_id, api_key=_subscription_api_key()
                )
                if _stripe_value(pending, "status") == "open":
                    url = _stripe_value(pending, "url")
                    if url:
                        return redirect(url)
                if _stripe_value(pending, "status") == "complete":
                    messages.info(request, "Your previous checkout is being processed. Please check your account before trying again.")
                    return redirect("student_dashboard")
                # Only expired sessions permit a new checkout.
                existing.pending_stripe_checkout_id = ""
                existing.save(update_fields=["pending_stripe_checkout_id"])
            session = stripe.checkout.Session.create(
                api_key=_subscription_api_key(),
                mode="subscription",
                payment_method_types=["card", "us_bank_account"],
                payment_method_options={"us_bank_account": {"verification_method": "automatic"}},
                customer_email=request.user.email or None,
                line_items=_annual_line_items(),
                success_url=request.build_absolute_uri("/subscription/stripe/success/") + "?session_id={CHECKOUT_SESSION_ID}",
                cancel_url=request.build_absolute_uri("/subscription/subscribe/"),
                metadata={"purpose": "pandaspeak_annual_subscription", "user_id": str(request.user.id)},
                subscription_data={"metadata": {"purpose": "pandaspeak_annual_subscription", "user_id": str(request.user.id)}},
                idempotency_key=f"pandaspeak-annual-{request.user.pk}-{django_timezone.now().strftime('%Y%m%d%H%M')}",
            )
            existing.pending_stripe_checkout_id = session.id
            existing.save(update_fields=["pending_stripe_checkout_id"])
            return redirect(session.url)
    except stripe.error.StripeError:
        messages.error(request, "Unable to verify or start Stripe checkout right now. Please try again later.")
        return redirect("subscribe")


@login_required
def stripe_plus_upgrade(request):
    if request.method != "POST":
        return redirect("plus_upgrade")
    local = Subscription.objects.filter(user=request.user).first()
    if local and local.is_disputed:
        return redirect("dispute_restricted")
    if not local or not local.is_active or local.is_cancelled:
        messages.error(request, "An active PandaSpeak Standard annual subscription is required before upgrading.")
        return redirect("subscribe")
    if local.plus_is_active:
        messages.info(request, "You already have PandaSpeak Plus.")
        return redirect("student_dashboard")
    try:
        session = stripe.checkout.Session.create(api_key=_subscription_api_key(), mode="subscription", payment_method_types=["card"], customer_email=request.user.email or None, line_items=[{"price": _plus_price(), "quantity": 1}], success_url=request.build_absolute_uri("/subscription/plus/success/") + "?session_id={CHECKOUT_SESSION_ID}", cancel_url=request.build_absolute_uri("/subscription/plus/upgrade/"), metadata={"purpose": "pandaspeak_plus_addon", "user_id": str(request.user.id)}, subscription_data={"metadata": {"purpose": "pandaspeak_plus_addon", "user_id": str(request.user.id)}})
        return redirect(session.url)
    except stripe.error.StripeError:
        messages.error(request, "Unable to start Plus checkout right now. Please try again.")
        return redirect("plus_upgrade")


@login_required
def stripe_subscription_success(request):
    session_id = request.GET.get("session_id")
    if session_id:
        try:
            session = stripe.checkout.Session.retrieve(session_id, api_key=_subscription_api_key())
            if _stripe_value(session, "payment_status") == "paid" and _stripe_value(_stripe_value(session, "metadata", {}) or {}, "user_id") == str(request.user.id):
                remote = stripe.Subscription.retrieve(_stripe_value(session, "subscription"), api_key=_subscription_api_key())
                _sync_base_from_stripe(remote, user=request.user, payment_confirmed=True)
        except stripe.error.StripeError:
            pass
    return redirect("student_dashboard")


@login_required
def stripe_plus_success(request):
    session_id = request.GET.get("session_id")
    if session_id:
        try:
            session = stripe.checkout.Session.retrieve(session_id, api_key=_subscription_api_key())
            if _stripe_value(session, "payment_status") == "paid" and _stripe_value(_stripe_value(session, "metadata", {}) or {}, "user_id") == str(request.user.id):
                remote = stripe.Subscription.retrieve(_stripe_value(session, "subscription"), api_key=_subscription_api_key())
                _sync_plus_from_stripe(remote, user=request.user, payment_confirmed=True)
        except stripe.error.StripeError:
            pass
    return redirect("student_dashboard")


@login_required
def dispute_restricted(request):
    local = Subscription.objects.filter(user=request.user).first()
    if not local or not local.is_disputed:
        return redirect("student_dashboard")
    return render(request, "subscription/dispute_restricted.html", {"subscription": local})


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
        if event_type == "charge.dispute.created":
            _record_subscription_dispute(obj)
        elif event_type in ("charge.dispute.updated", "charge.dispute.closed"):
            _update_subscription_dispute_status(obj)
        elif event_type == "invoice.created":
            _apply_reward_to_upcoming_plus_invoice(obj)
        elif event_type in ("checkout.session.completed", "checkout.session.async_payment_succeeded"):
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
                    if confirmed:
                        _consume_reward_from_paid_invoice(obj)
                elif purpose == "pandaspeak_annual_subscription":
                    _sync_base_from_stripe(remote, payment_confirmed=confirmed)
    except stripe.error.StripeError:
        return HttpResponse(status=500)
    return HttpResponse(status=200)
