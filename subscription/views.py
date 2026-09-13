from datetime import datetime, timezone

from django.shortcuts import render, redirect
from django.conf import settings
from django.contrib.auth.decorators import login_required
from .models import Subscription, TutoringPayment
import stripe
import requests
from django.contrib import messages
from django.utils.dateparse import parse_datetime
from django.core.mail import send_mail


stripe.api_key = settings.STRIPE_SECRET_KEY


def _paypal_access_token():
    if not settings.PAYPAL_BASE_URL or not settings.PAYPAL_CLIENT_ID or not settings.PAYPAL_SECRET:
        return None

    response = requests.post(
        f"{settings.PAYPAL_BASE_URL}/v1/oauth2/token",
        auth=(settings.PAYPAL_CLIENT_ID, settings.PAYPAL_SECRET),
        data={"grant_type": "client_credentials"},
        timeout=20,
    )
    if response.status_code != 200:
        return None
    return response.json().get("access_token")


def _paypal_headers(access_token):
    return {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }


def _get_or_create_paypal_product(access_token):
    headers = _paypal_headers(access_token)
    list_response = requests.get(
        f"{settings.PAYPAL_BASE_URL}/v1/catalogs/products",
        headers=headers,
        params={"page_size": 20, "total_required": "true"},
        timeout=20,
    )
    if list_response.status_code == 200:
        for product in list_response.json().get("products", []):
            if product.get("name") == "PandaSpeak Annual Subscription":
                return product.get("id")

    create_response = requests.post(
        f"{settings.PAYPAL_BASE_URL}/v1/catalogs/products",
        headers=headers,
        json={
            "name": "PandaSpeak Annual Subscription",
            "description": "Annual access to PandaSpeak Chinese learning materials.",
            "type": "SERVICE",
            "category": "EDUCATIONAL_AND_TEXTBOOKS",
        },
        timeout=20,
    )
    if create_response.status_code not in (200, 201):
        return None
    return create_response.json().get("id")


def _get_or_create_paypal_plan(access_token, product_id):
    headers = _paypal_headers(access_token)
    list_response = requests.get(
        f"{settings.PAYPAL_BASE_URL}/v1/billing/plans",
        headers=headers,
        params={"product_id": product_id, "page_size": 20, "total_required": "true"},
        timeout=20,
    )
    if list_response.status_code == 200:
        for plan in list_response.json().get("plans", []):
            if plan.get("name") == "PandaSpeak Yearly $15" and plan.get("status") == "ACTIVE":
                return plan.get("id")

    create_response = requests.post(
        f"{settings.PAYPAL_BASE_URL}/v1/billing/plans",
        headers=headers,
        json={
            "product_id": product_id,
            "name": "PandaSpeak Yearly $15",
            "description": "PandaSpeak annual subscription - $15 per year.",
            "status": "ACTIVE",
            "billing_cycles": [
                {
                    "frequency": {
                        "interval_unit": "YEAR",
                        "interval_count": 1,
                    },
                    "tenure_type": "REGULAR",
                    "sequence": 1,
                    "total_cycles": 0,
                    "pricing_scheme": {
                        "fixed_price": {
                            "value": "15.00",
                            "currency_code": "USD",
                        }
                    },
                }
            ],
            "payment_preferences": {
                "auto_bill_outstanding": True,
                "payment_failure_threshold": 1,
            },
        },
        timeout=20,
    )
    if create_response.status_code not in (200, 201):
        return None
    return create_response.json().get("id")


def _start_stripe_subscription_checkout(request):
    try:
        checkout_session = stripe.checkout.Session.create(
            mode="subscription",
            payment_method_types=["card"],
            customer_email=request.user.email or None,
            line_items=[
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
            ],
            success_url=(
                request.build_absolute_uri("/subscription/success/")
                + "?stripe_session_id={CHECKOUT_SESSION_ID}"
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


@login_required
def subscribe(request):
    if request.method == "POST":
        if request.POST.get("subscription_type") != "yearly":
            messages.error(request, "Please choose a valid subscription plan.")
            return redirect("subscribe")

        payment_method = request.POST.get("payment_method", "paypal")
        if payment_method == "stripe":
            return _start_stripe_subscription_checkout(request)

        if payment_method != "paypal":
            messages.error(request, "Please choose a valid payment method.")
            return redirect("subscribe")

        try:
            access_token = _paypal_access_token()
            if not access_token:
                messages.error(request, "Unable to connect to PayPal right now. Please try again.")
                return redirect("subscribe")

            product_id = _get_or_create_paypal_product(access_token)
            if not product_id:
                messages.error(request, "Unable to prepare the PayPal subscription product.")
                return redirect("subscribe")

            plan_id = _get_or_create_paypal_plan(access_token, product_id)
            if not plan_id:
                messages.error(request, "Unable to prepare the PayPal yearly subscription plan.")
                return redirect("subscribe")

            subscription_response = requests.post(
                f"{settings.PAYPAL_BASE_URL}/v1/billing/subscriptions",
                headers=_paypal_headers(access_token),
                json={
                    "plan_id": plan_id,
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

            if subscription_response.status_code not in (200, 201):
                messages.error(request, "PayPal could not start the subscription checkout. Please try again.")
                return redirect("subscribe")

            paypal_data = subscription_response.json()
            approval_url = next(
                (link.get("href") for link in paypal_data.get("links", []) if link.get("rel") == "approve"),
                None,
            )
            if not approval_url:
                messages.error(request, "PayPal did not return an approval page. Please try again.")
                return redirect("subscribe")

            return redirect(approval_url)
        except requests.RequestException:
            messages.error(request, "Unable to reach PayPal right now. Please try again.")
            return redirect("subscribe")

    return render(request, "subscription/subscribe.html")


@login_required
def subscription_success(request):
    stripe_session_id = request.GET.get("stripe_session_id", "")
    if stripe_session_id:
        try:
            checkout_session = stripe.checkout.Session.retrieve(stripe_session_id)
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

        stripe_subscription_id = checkout_session.get("subscription")
        access_until = None
        try:
            stripe_subscription = stripe.Subscription.retrieve(stripe_subscription_id)
            current_period_end = stripe_subscription.get("current_period_end")
            if current_period_end:
                access_until = datetime.fromtimestamp(current_period_end, tz=timezone.utc)
        except stripe.error.StripeError:
            pass

        Subscription.objects.update_or_create(
            user=request.user,
            defaults={
                "subscription_plan": "standard",
                "subscription_cost": 15.00,
                "paypal_subscription_id": None,
                "stripe_subscription_id": stripe_subscription_id,
                "is_active": True,
                "is_cancelled": False,
                "access_until": access_until,
            },
        )
    else:
        paypal_subscription_id = request.GET.get("subscription_id", "")
        if not paypal_subscription_id:
            messages.error(request, "The payment provider did not return a subscription ID. Please contact PandaSpeak support if you were charged.")
            return redirect("subscribe")

        Subscription.objects.update_or_create(
            user=request.user,
            defaults={
                "subscription_plan": "standard",
                "subscription_cost": 15.00,
                "paypal_subscription_id": paypal_subscription_id,
                "stripe_subscription_id": None,
                "is_active": True,
                "is_cancelled": False,
            },
        )

    context = {
        "user": request.user,
        "first_name": request.user.first_name,
    }
    return render(request, "subscription/success.html", context)


@login_required
def cancel_subscription(request):
    if request.method != "POST":
        return redirect("account_management_student")

    try:
        subscription = Subscription.objects.get(user=request.user, is_active=True)
    except Subscription.DoesNotExist:
        messages.error(request, "No active subscription found.")
        return redirect("account_management_student")

    if subscription.stripe_subscription_id:
        try:
            stripe_subscription = stripe.Subscription.modify(
                subscription.stripe_subscription_id,
                cancel_at_period_end=True,
            )
            current_period_end = stripe_subscription.get("current_period_end")
            if current_period_end:
                subscription.access_until = datetime.fromtimestamp(current_period_end, tz=timezone.utc)
            subscription.is_cancelled = True
            subscription.save(update_fields=["is_cancelled", "access_until"])
        except stripe.error.StripeError:
            messages.error(request, "There was an error canceling your subscription. Please try again later.")
            return redirect("account_management_student")

        student_name = request.user.get_full_name() or request.user.username
        send_mail(
            subject="PandaSpeak Subscription Cancellation Confirmation",
            message=(
                f"A student has cancelled their PandaSpeak subscription.\n\n"
                f"Student: {student_name}\n"
                f"Email: {request.user.email}\n"
                f"Account Type: Student\n"
                f"Stripe Subscription ID: {subscription.stripe_subscription_id}\n"
                f"Access until: {subscription.access_until}\n\n"
            ),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[settings.EMAIL_HOST_USER],
            fail_silently=False,
        )
        messages.success(
            request,
            "Your subscription has been canceled successfully. "
            "You will not be charged for the next billing cycle, and you will retain access until the end of your current subscription period.",
        )
        return redirect("account_management_student")

    if not subscription.paypal_subscription_id:
        messages.error(request, "No payment-provider subscription ID found.")
        return redirect("account_management_student")

    auth_response = requests.post(
        f"{settings.PAYPAL_BASE_URL}/v1/oauth2/token",
        auth=(settings.PAYPAL_CLIENT_ID, settings.PAYPAL_SECRET),
        data={"grant_type": "client_credentials"},
    )
    if auth_response.status_code != 200:
        messages.error(request, "Unable to connect to PayPal.")
        return redirect("account_management_student")

    access_token = auth_response.json()["access_token"]

    details_response = requests.get(
        f"{settings.PAYPAL_BASE_URL}/v1/billing/subscriptions/{subscription.paypal_subscription_id}",
        headers={
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        },
    )
    if details_response.status_code == 200:
        paypal_data = details_response.json()
        next_billing_time = paypal_data.get("billing_info", {}).get("next_billing_time")
        if next_billing_time:
            subscription.access_until = parse_datetime(next_billing_time)

    cancel_response = requests.post(
        f"{settings.PAYPAL_BASE_URL}/v1/billing/subscriptions/{subscription.paypal_subscription_id}/cancel",
        headers={
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        },
        json={"reason": "User requested cancellation."},
    )

    if cancel_response.status_code == 204:
        subscription.is_cancelled = True
        subscription.save()

        student_name = request.user.get_full_name() or request.user.username
        send_mail(
            subject="PandaSpeak Subscription Cancellation Confirmation",
            message=(
                f"A student has cancelled their PandaSpeak subscription.\n\n"
                f"Student: {student_name}\n"
                f"Email: {request.user.email}\n"
                f"Account Type: Student\n"
                f"PayPal Subscription ID: {subscription.paypal_subscription_id}\n"
                f"Access until: {subscription.access_until}\n\n"
            ),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[settings.EMAIL_HOST_USER],
            fail_silently=False,
        )
        messages.success(
            request,
            "Your subscription has been canceled successfully. "
            "You will not be charged for the next billing cycle, and you will retain access until the end of your current subscription period.",
        )
    else:
        messages.error(request, "There was an error canceling your subscription. Please try again later.")
    return redirect("account_management_student")


@login_required
def create_tutoring_checkout_session(request, payment_id):
    payment = TutoringPayment.objects.get(id=payment_id, student_name=request.user)
    unit_amount = int(payment.amount * 100)
    checkout_data = {
        "payment_method_types": ["card"],
        "mode": "payment",
        "line_items": [{
            "price_data": {
                "currency": "usd",
                "product_data": {
                    "name": f"Payment for {payment.class_name} tutoring session",
                },
                "unit_amount": unit_amount,
            },
            "quantity": 1,
        }],
        "success_url": request.build_absolute_uri("/subscription/tutoring-payment-success/") + "?session_id={CHECKOUT_SESSION_ID}",
        "cancel_url": request.build_absolute_uri("/subscription/tutoring-payment-cancelled/"),
        "metadata": {
            "payment_id": payment.id,
            "user_id": payment.user.id,
            "teacher_id": payment.teacher.id,
        },
    }

    # If the teacher has a connected Stripe account, set up the payment to transfer funds to them
    if payment.teacher.stripe_account_id:
        application_fee_amount = int(unit_amount * float(payment.platform_fee_percent) / 100)
        checkout_data["payment_intent_data"] = {
            "application_fee_amount": application_fee_amount,
            "transfer_data": {
                "destination": payment.teacher.stripe_account_id,
            },
        }
    checkout_session = stripe.checkout.Session.create(**checkout_data)
    return redirect(checkout_session.url)
