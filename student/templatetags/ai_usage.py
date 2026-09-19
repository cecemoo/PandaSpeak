from datetime import timedelta

from django import template
from django.db.models import Count, Sum
from django.db.models.functions import Coalesce
from django.utils import timezone

from student.models import AIConversationUsage

register = template.Library()


def _summary(queryset):
    totals = queryset.aggregate(
        events=Count("id"),
        estimated_cost=Coalesce(Sum("estimated_cost_usd"), 0),
    )
    return {
        "events": totals["events"] or 0,
        "estimated_cost": totals["estimated_cost"] or 0,
        "replies": queryset.filter(kind="reply").count(),
        "speech": queryset.filter(kind="speech").count(),
        "cached_speech": queryset.filter(kind="speech", cached=True).count(),
        "students": queryset.values("student_id").distinct().count(),
    }


@register.simple_tag
def ai_usage_summary():
    """Manager-facing AI usage/cost snapshot for measuring real PandaSpeak usage."""
    now = timezone.now()
    today = timezone.localdate()
    today_start = timezone.make_aware(
        timezone.datetime.combine(today, timezone.datetime.min.time()),
        timezone.get_current_timezone(),
    )
    month_start = today_start.replace(day=1)

    all_usage = AIConversationUsage.objects.all()
    return {
        "today": _summary(all_usage.filter(created_at__gte=today_start)),
        "month": _summary(all_usage.filter(created_at__gte=month_start)),
        "all": _summary(all_usage),
        "generated_at": now,
    }
