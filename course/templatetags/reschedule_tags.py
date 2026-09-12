from datetime import timedelta

from django import template
from django.utils import timezone

register = template.Library()


@register.filter
def can_reschedule(booking):
    return bool(
        booking
        and booking.status == "confirmed"
        and booking.session_status == "scheduled"
        and booking.timeslot.start_time > timezone.now() + timedelta(hours=24)
    )


@register.filter
def is_reschedule_party(booking, user):
    if not booking or not user or not getattr(user, "is_authenticated", False):
        return False
    return (
        booking.student_id == user.id
        or booking.timeslot.course.teacher_id == user.id
    )
