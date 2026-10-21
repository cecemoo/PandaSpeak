from django.shortcuts import redirect
from functools import wraps
from .models import Subscription
from .plan_access import has_base_access


def subscription_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect("login")

        # Staff and superusers need unrestricted access to manage and test PandaSpeak.
        if request.user.is_staff or request.user.is_superuser:
            return view_func(request, *args, **kwargs)

        subscription = Subscription.objects.filter(user=request.user).first()
        if subscription and subscription.is_disputed:
            return redirect("dispute_restricted")

        if not has_base_access(request.user):
            return redirect("subscription_plans")

        return view_func(request, *args, **kwargs)
    return wrapper
