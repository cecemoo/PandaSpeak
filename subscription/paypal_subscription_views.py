from django.conf import settings
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.utils import timezone
from django.utils.dateparse import parse_datetime
from django.views.decorators.csrf import csrf_exempt
import requests

from .models import Subscription
from .views import _paypal_access_token, _paypal_headers, _get_or_create_paypal_product, _get_or_create_paypal_plan

User = get_user_model()


def _paypal_subscription_details(subscription_id, access_token=None):
    access_token = access_token or _paypal_access_token()
    if not access_token or not subscription_id:
        return None
    try:
        response = requests.get(
            f"{settings.PAYPAL_BASE_URL}/v1/billing/subscriptions/{subscription_id}",
            headers=_paypal_headers(access_token),
            timeout=20,
        )
    except requests.RequestException:
        return None
    if response.status_code != 200:
        return None
    return response.json()


def _sync_verified_paypal_subscription(data, expected_user=None):
    """Sync only data fetched directly from PayPal, never browser-supplied status."""
    subscription_id = data.get("id")
    custom_id = str(data.get("custom_id") or "")
    status = str(data.get("status") or "").upper()
    if not subscription_id or not custom_id:
        return None

    try:
        user = expected_user or User.objects.get(pk=custom_id)
    except (User.DoesNotExist, ValueError, TypeError):
        return None
    if str(user.pk) != custom_id:
        return None

    existing = Subscription.objects.filter(user=user).first()
    if existing and existing.stripe_subscription_id and existing.is_active and not existing.is_cancelled:
        return None
    if existing and existing.paypal_subscription_id and existing.paypal_subscription_id != subscription_id and existing.is_active and not existing.is_cancelled:
        return None

    billing_info = data.get("billing_info") or {}
    next_billing_time = parse_datetime(billing_info.get("next_billing_time") or "")
    active = status in ("ACTIVE", "APPROVED")
    cancelled = status in ("CANCELLED", "SUSPENDED", "EXPIRED")

    subscription, _ = Subscription.objects.update_or_create(
        user=user,
        defaults={
            "subscription_plan": "standard",
            "subscription_cost": 15.00,
            "paypal_subscription_id": subscription_id,
            "stripe_subscription_id": None,
            "is_active": active,
            "is_cancelled": cancelled,
            "access_until": next_billing_time or (existing.access_until if existing else None),
        },
    )
    return subscription


@login_required
def paypal_subscription_checkout(request):
    if request.method != "POST":
        return redirect("subscribe")
    if request.POST.get("subscription_type") != "yearly":
        messages.error(request, "Please choose a valid subscription plan.")
        return redirect("subscribe")

    try:
        access_token = _paypal_access_token()
        if not access_token:
            raise requests.RequestException("No PayPal access token")
        product_id = _get_or_create_paypal_product(access_token)
        plan_id = _get_or_create_paypal_plan(access_token, product_id) if product_id else None
        if not plan_id:
            messages.error(request, "Unable to prepare PayPal checkout right now. Please try again.")
            return redirect("subscribe")

        response = requests.post(
            f"{settings.PAYPAL_BASE_URL}/v1/billing/subscriptions",
            headers=_paypal_headers(access_token),
            json={
                "plan_id": plan_id,
                "custom_id": str(request.user.pk),
                "subscriber": {
                    "name": {
                        "given_name": request.user.first_name or "PandaSpeak",
                        "surname": request.user.last_name or "Student",
                    },
                    "email_address": request.user.email,
                },
                "application_context": {
                    "brand_name": "PandaSpeak",
                    "locale": "en-US",
                    "shipping_preference": "NO_SHIPPING",
                    "user_action": "SUBSCRIBE_NOW",
                    "return_url": request.build_absolute_uri("/subscription/success/"),
                    "cancel_url": request.build_absolute_uri("/subscription/subscribe/"),
                },
            },
            timeout=20,
        )
        if response.status_code not in (200, 201):
            messages.error(request, "PayPal could not start the subscription checkout. Please try again.")
            return redirect("subscribe")
        data = response.json()
        approval_url = next((x.get("href") for x in data.get("links", []) if x.get("rel") == "approve"), None)
        if not approval_url:
            messages.error(request, "PayPal did not return an approval page. Please try again.")
            return redirect("subscribe")
        return redirect(approval_url)
    except requests.RequestException:
        messages.error(request, "Unable to reach PayPal right now. Please try again.")
        return redirect("subscribe")


@login_required
def paypal_subscription_success(request):
    subscription_id = request.GET.get("subscription_id", "")
    if not subscription_id:
        messages.error(request, "PayPal did not return a subscription ID. If you were charged, please contact PandaSpeak support.")
        return redirect("subscribe")

    data = _paypal_subscription_details(subscription_id)
    if not data or str(data.get("custom_id") or "") != str(request.user.pk) or str(data.get("status") or "").upper() not in ("ACTIVE", "APPROVED"):
        messages.error(request, "We could not verify an active PayPal subscription yet. If PayPal completed your payment, please wait briefly and sign in again or contact PandaSpeak support.")
        return redirect("subscribe")

    subscription = _sync_verified_paypal_subscription(data, expected_user=request.user)
    if not subscription or not subscription.is_active:
        messages.error(request, "PayPal confirmed the subscription, but PandaSpeak could not enable access. Please contact support.")
        return redirect("subscribe")

    return render(request, "subscription/success.html", {"user": request.user, "first_name": request.user.first_name})


def _verify_paypal_webhook(event, request, access_token):
    webhook_id = getattr(settings, "PAYPAL_WEBHOOK_ID", "")
    if not webhook_id:
        return False
    payload = {
        "transmission_id": request.META.get("HTTP_PAYPAL_TRANSMISSION_ID", ""),
        "transmission_time": request.META.get("HTTP_PAYPAL_TRANSMISSION_TIME", ""),
        "cert_url": request.META.get("HTTP_PAYPAL_CERT_URL", ""),
        "auth_algo": request.META.get("HTTP_PAYPAL_AUTH_ALGO", ""),
        "transmission_sig": request.META.get("HTTP_PAYPAL_TRANSMISSION_SIG", ""),
        "webhook_id": webhook_id,
        "webhook_event": event,
    }
    try:
        response = requests.post(
            f"{settings.PAYPAL_BASE_URL}/v1/notifications/verify-webhook-signature",
            headers=_paypal_headers(access_token),
            json=payload,
            timeout=20,
        )
    except requests.RequestException:
        return None
    if response.status_code != 200:
        return None
    return response.json().get("verification_status") == "SUCCESS"


@csrf_exempt
def paypal_subscription_webhook(request):
    if request.method != "POST":
        return HttpResponse(status=405)
    try:
        event = request.json if hasattr(request, "json") else None
        if event is None:
            import json
            event = json.loads(request.body.decode("utf-8"))
    except (ValueError, UnicodeDecodeError):
        return HttpResponse(status=400)

    access_token = _paypal_access_token()
    if not access_token:
        return HttpResponse(status=503)
    verified = _verify_paypal_webhook(event, request, access_token)
    if verified is None:
        return HttpResponse(status=503)  # transient verification failure: ask PayPal to retry
    if not verified:
        return HttpResponse(status=400)

    event_type = event.get("event_type", "")
    resource = event.get("resource") or {}
    subscription_id = None
    if event_type.startswith("BILLING.SUBSCRIPTION."):
        subscription_id = resource.get("id")
    elif event_type == "PAYMENT.SALE.COMPLETED":
        subscription_id = resource.get("billing_agreement_id")

    if subscription_id:
        data = _paypal_subscription_details(subscription_id, access_token=access_token)
        if data:
            _sync_verified_paypal_subscription(data)
        elif event_type in ("BILLING.SUBSCRIPTION.ACTIVATED", "PAYMENT.SALE.COMPLETED"):
            return HttpResponse(status=500)  # PayPal retries; do not lose paid activation

    return HttpResponse(status=200)
