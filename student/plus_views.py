from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from subscription.models import Subscription
from subscription.plan_access import plan_features


@login_required(login_url='my_login')
def plus_upgrade(request):
    """Show PandaSpeak Plus only after a student has an active subscription."""
    subscription = Subscription.objects.filter(user=request.user).first()
    if not subscription or not subscription.is_active or subscription.is_cancelled:
        messages.info(
            request,
            "PandaSpeak Plus is an optional upgrade for active PandaSpeak subscribers. Please subscribe to PandaSpeak Standard first.",
        )
        return redirect('subscribe')

    features = plan_features(request.user)
    return render(
        request,
        'student/plus_upgrade.html',
        {'plan_features': features, 'subscription': subscription},
    )
