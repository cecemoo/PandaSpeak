from django import template


register = template.Library()


@register.filter
def tutoring_session_visible(booking):
    """Return False once a completed paid session has aged out of dashboards."""
    return not booking.is_archived_from_tutoring_lists
