from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Count, Max, Q
from django.shortcuts import render

from .models import StudentActivity, Subscription


def _manager(user):
    return user.is_authenticated and (user.is_staff or user.is_superuser)


@login_required
@user_passes_test(_manager)
def student_activity(request):
    query = (request.GET.get("q") or "").strip()
    selected_user_id = request.GET.get("student") or ""

    subscriptions = (
        Subscription.objects.select_related("user")
        .filter(user__is_teacher=False, user__is_staff=False)
        .annotate(last_activity=Max("user__student_activities__created_at"), activity_count=Count("user__student_activities"))
        .order_by("-last_activity", "user__email")
    )
    if query:
        subscriptions = subscriptions.filter(
            Q(user__email__icontains=query)
            | Q(user__first_name__icontains=query)
            | Q(user__last_name__icontains=query)
        )

    activities = StudentActivity.objects.select_related("user")
    selected_subscription = None
    if selected_user_id:
        selected_subscription = subscriptions.filter(user_id=selected_user_id).first()
        if selected_subscription:
            activities = activities.filter(user_id=selected_subscription.user_id)
    else:
        activities = activities.none()

    return render(
        request,
        "subscription/manager_student_activity.html",
        {
            "subscriptions": subscriptions[:200],
            "activities": activities[:500],
            "selected_subscription": selected_subscription,
            "query": query,
        },
    )
