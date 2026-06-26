from django.shortcuts import render, redirect
from django.conf import settings
from django.contrib.auth.decorators import login_required
from .models import Subscription, TutoringPayment
import stripe


stripe.api_key = settings.STRIPE_SECRET_KEY


@login_required
def subscribe(request):
    return render(request, "subscription/subscribe.html")


@login_required
def subscription_success(request):
    paypal_subscription_id = request.GET.get("subscription_id", "")
    Subscription.objects.update_or_create(
        user=request.user,
        defaults={
            "subscription_plan": "standard",
            "subscription_cost": 12.94,
            "paypal_subscription_id": paypal_subscription_id,
            "is_active": True,
            },
    )
    context = {
        "user": request.user,
        "first_name": request.user.first_name,
    }
    return render(request, "subscription/success.html", context)


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