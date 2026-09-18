from django import template

from course.models import GroupClassRequest

register = template.Library()


@register.simple_tag
def student_group_requests(user):
    """Return the current student's group-class requests, newest first."""
    if not getattr(user, "is_authenticated", False):
        return GroupClassRequest.objects.none()
    return (
        GroupClassRequest.objects
        .filter(student=user)
        .select_related("teacher")
        .order_by("-created_at")
    )
