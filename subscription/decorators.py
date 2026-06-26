from django.shortcuts import redirect
from functools import wraps
from .models import Subscription



def subscription_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect("login")
        
        has_subscription = Subscription.objects.filter(
            user=request.user,
            is_active=True
        ).exists()

        if not has_subscription:
            return redirect("subscribe")
        
        return view_func(request, *args, **kwargs)
    return wrapper
