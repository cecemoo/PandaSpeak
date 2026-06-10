from django.shortcuts import render, redirect
from django.conf import settings
from django.contrib.auth.decorators import login_required
from .models import UserSubscription
import stripe

# Create your views here.


stripe.api_key = settings.STRIPE_SECRET_KEY


@login_required
def subscribe(request):
    return render(request, "subscription/subscribe.html")

@login_required
def create_checkout_session(request):
    checkout_session = stripe.checkout.Session.create(
        payment_method_types=["card"],
        mode="subscription",
        customer_email=request.user.email,
        line_items=[
            {
                "price": settings.STRIPE_PRICE_ID,
                "quantity": 1,
            }
        ],
        success_url=request.build_absolute_uri("/subscription/success/"),
        cancel_url=request.build_absolute_uri("/subscription/subscribe/"),
        metadata={
            "user_id": request.user.id,
        }
    )
    return redirect(checkout_session.url)


@login_required
def subscription_success(request):
    UserSubscription.objects.update_or_create(
        user=request.user,
        defaults={"is_active": True},
    )
    return render(request, "subscription/success.html")
