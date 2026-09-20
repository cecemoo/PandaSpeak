from datetime import datetime, timezone

import stripe
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect

from .models import Subscription
from .views import cancel_subscription as legacy_cancel_subscription


def _api_key():
    return getattr(settings, 'STRIPE_SUBSCRIPTION_SECRET_KEY', '') or settings.STRIPE_SECRET_KEY


@login_required
def cancel_plus(request):
    """Turn off Plus renewal only; annual Standard membership is untouched."""
    if request.method != 'POST':
        return redirect('account_management_student')
    subscription = Subscription.objects.filter(user=request.user, is_active=True).first()
    if not subscription or not subscription.plus_stripe_subscription_id or not subscription.plus_is_active:
        messages.info(request, 'You do not have an active PandaSpeak Plus add-on to cancel.')
        return redirect('account_management_student')
    try:
        remote = stripe.Subscription.modify(
            subscription.plus_stripe_subscription_id,
            cancel_at_period_end=True,
            api_key=_api_key(),
        )
    except stripe.error.StripeError:
        messages.error(request, 'There was an error canceling PandaSpeak Plus. Please try again later.')
        return redirect('account_management_student')
    period_end = remote.get('current_period_end')
    if period_end:
        subscription.plus_access_until = datetime.fromtimestamp(period_end, tz=timezone.utc)
    subscription.plus_is_cancelled = True
    subscription.save(update_fields=['plus_is_cancelled', 'plus_access_until'])
    messages.success(request, 'PandaSpeak Plus will end after your current paid month. This month is nonrefundable. Your $15 annual PandaSpeak subscription remains active and will continue to renew unless you cancel it separately.')
    return redirect('account_management_student')


@login_required
def cancel_subscription(request):
    """Cancel only the base annual membership renewal."""
    if request.method != 'POST':
        return redirect('account_management_student')

    subscription = Subscription.objects.filter(user=request.user, is_active=True).first()
    if not subscription or not subscription.stripe_subscription_id:
        return legacy_cancel_subscription(request)

    try:
        remote = stripe.Subscription.modify(
            subscription.stripe_subscription_id,
            cancel_at_period_end=True,
            api_key=_api_key(),
        )
    except stripe.error.StripeError:
        messages.error(request, 'There was an error canceling your annual subscription. Please try again later.')
        return redirect('account_management_student')

    period_end = remote.get('current_period_end')
    if period_end:
        subscription.access_until = datetime.fromtimestamp(period_end, tz=timezone.utc)
    subscription.is_cancelled = True
    subscription.save(update_fields=['is_cancelled', 'access_until'])
    messages.success(request, 'Your $15 annual subscription renewal has been canceled. The current annual payment is nonrefundable and access remains available through the paid period.')
    return redirect('account_management_student')
