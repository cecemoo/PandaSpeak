from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from subscription.models import Subscription


@login_required(login_url='my_login')
def subscription_plans(request):
    """Show PayPal plans only to students without an active subscription."""
    subscription = Subscription.objects.filter(user=request.user).first()

    if subscription and subscription.is_active:
        return redirect('account_management_student')

    return render(request, 'student/subscription_plans.html')


@login_required(login_url='my_login')
def account_management(request):
    """Show the student's current subscription record and status."""
    subscription = Subscription.objects.filter(user=request.user).first()

    context = {
        'has_subscription': subscription is not None,
        'subscription_active': bool(subscription and subscription.is_active),
        'SubPlan': subscription.subscription_plan if subscription else 'No subscription',
        'subscription_cost': subscription.subscription_cost if subscription else None,
        'is_cancelled': subscription.is_cancelled if subscription else False,
        'access_until': subscription.access_until if subscription else None,
    }
    return render(request, 'student/account_management.html', context)
