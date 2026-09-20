from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from subscription.plan_access import plan_features


@login_required(login_url='my_login')
def plus_upgrade(request):
    """Preview PandaSpeak Plus before the second Stripe price is connected."""
    features = plan_features(request.user)
    return render(request, 'student/plus_upgrade.html', {'plan_features': features})
