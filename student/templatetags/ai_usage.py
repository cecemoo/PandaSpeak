from datetime import datetime, time
from decimal import Decimal

from django import template
from django.db.models import Count, Sum, Value
from django.db.models.functions import Coalesce
from django.db.models.fields import DecimalField
from django.utils import timezone

from student.models import AIConversationUsage

register = template.Library()


def _summary(queryset):
    totals = queryset.aggregate(
        events=Count("id"),
        estimated_cost=Coalesce(
            Sum("estimated_cost_usd"),
            Value(Decimal("0.000000")),
            output_field=DecimalField(max_digits=10, decimal_places=6),
        ),
    )
    return {
        "events": totals["events"] or 0,
        "estimated_cost": totals["estimated_cost"] or Decimal("0"),
        "replies": queryset.filter(kind="reply").count(),
        "speech": queryset.filter(kind="speech").count(),
        "cached_speech": queryset.filter(kind="speech", cached=True).count(),
        "students": queryset.values("student_id").distinct().count(),
    }


@register.simple_tag
def ai_usage_summary():
    """Manager-facing AI usage/cost snapshot for measuring real PandaSpeak usage."""
    today = timezone.localdate()
    today_start = timezone.make_aware(
        datetime.combine(today, time.min),
        timezone.get_current_timezone(),
    )
    month_start = today_start.replace(day=1)

    all_usage = AIConversationUsage.objects.all()
    return {
        "today": _summary(all_usage.filter(created_at__gte=today_start)),
        "month": _summary(all_usage.filter(created_at__gte=month_start)),
        "all": _summary(all_usage),
    }
