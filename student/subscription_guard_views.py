from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect

from subscription.subscription_guard_views import _has_current_subscription
from . import views


@login_required(login_url='my_login')
def guarded_subscription_plans(request):
    """Do not show subscription plans to students who already have paid access."""
    if _has_current_subscription(request.user):
        return redirect('account_management_student')
    return views.subscription_plans(request)
