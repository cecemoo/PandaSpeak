from datetime import timedelta

from django import template
from django.utils import timezone

from course.models import Booking


register = template.Library()


@register.inclusion_tag('student/_tutoring_sessions.html', takes_context=True)
def student_tutoring_sessions(context):
    request = context.get('request')
    if not request or not request.user.is_authenticated:
        return {'tutoring_sessions': []}

    now = timezone.now()
    bookings = list(
        Booking.objects.filter(
            student=request.user,
            status='confirmed',
            is_refunded=False,
        )
        .select_related('timeslot__course__teacher', 'timeslot__course')
        .order_by('timeslot__start_time')[:5]
    )

    tutoring_sessions = []
    for booking in bookings:
        open_at = booking.timeslot.start_time - timedelta(minutes=15)
        close_at = booking.timeslot.end_time + timedelta(minutes=30)
        booking.can_enter_classroom = open_at <= now <= close_at
        booking.classroom_opens_at = open_at
        tutoring_sessions.append(booking)

    return {
        'tutoring_sessions': tutoring_sessions,
        'now': now,
    }
