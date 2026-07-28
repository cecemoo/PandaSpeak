from django.shortcuts import redirect
from functools import wraps
from subscription.models import Subscription
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError
from django.utils import timezone
from django.conf import settings




def subscription_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('my_login')
        
        if not Subscription.objects.filter(user=request.user, is_active=True).exists():
            return redirect('subscription_plans')
        
        return view_func(request, *args, **kwargs)
    return wrapper



def add_teacher_local_times(bookings):

    for booking in bookings:

        timezone_name = (

            booking.timeslot.course.teacher_timezone

            or settings.TIME_ZONE

        )

        try:

            teacher_tz = ZoneInfo(timezone_name)

        except ZoneInfoNotFoundError:

            teacher_tz = ZoneInfo(settings.TIME_ZONE)

        booking.teacher_local_start = timezone.localtime(

            booking.timeslot.start_time,

            teacher_tz,

        )

        booking.teacher_local_end = timezone.localtime(

            booking.timeslot.end_time,

            teacher_tz,

        )

        booking.teacher_timezone_name = timezone_name

    return bookings