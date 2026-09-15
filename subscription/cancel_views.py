from datetime import datetime, timezone

import stripe
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect

from .models import Subscription
from .views import cancel_subscription as legacy_cancel_subscription


@login_required
def cancel_subscription(request):
    if request.method != 'POST':
        return redirect('account_management_student')

    subscription = Subscription.objects.filter(user=request.user, is_active=True).first()
    if not subscription or not subscription.stripe_subscription_id:
        return legacy_cancel_subscription(request)

    api_key = getattr(settings, 'STRIPE_SUBSCRIPTION_SECRET_KEY', '') or settings.STRIPE_SECRET_KEY
    try:
        remote = stripe.Subscription.modify(
            subscription.stripe_subscription_id,
            cancel_at_period_end=True,
            api_key=api_key,
        )
    except stripe.error.StripeError:
        messages.error(request, 'There was an error canceling your subscription. Please try again later.')
        return redirect('account_management_student')

    period_end = remote.get('current_period_end')
    if period_end:
        subscription.access_until = datetime.fromtimestamp(period_end, tz=timezone.utc)
    subscription.is_cancelled = True
    subscription.save(update_fields=['is_cancelled', 'access_until'])
    messages.success(request, 'Your subscription has been canceled successfully. You will not be charged for the next billing cycle, and you will retain access until the end of your current subscription period.')
    return redirect('account_management_student')
