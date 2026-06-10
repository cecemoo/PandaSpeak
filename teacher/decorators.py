from django.shortcuts import redirect
from functools import wraps
from student.models import Subscription


def subscription_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('my_login')
        
        if not Subscription.objects.filter(user=request.user, is_active=True).exists():
            return redirect('subscription_plans')
        
        return view_func(request, *args, **kwargs)
    return wrapper