from django.shortcuts import redirect
from functools import wraps
from .models import Subscription


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

        if not subscription or not subscription.is_active:
            return redirect("subscription_plans")

        return view_func(request, *args, **kwargs)
    return wrapper
