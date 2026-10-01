import stripe
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Count, Max, Q
from django.shortcuts import redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from .models import StudentActivity, Subscription
from . import stripe_subscription_views


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


@login_required
@user_passes_test(_manager)
@require_POST
def sync_existing_stripe_dispute(request, user_id):
    """Verify an existing Stripe dispute and attach it to the correct student.

    This is for disputes that began before the webhook destination subscribed to
    charge.dispute.* events. The Stripe dispute ID is verified server-side and
    must map back to this exact PandaSpeak annual subscription before access is
    changed.
    """
    local = Subscription.objects.select_related("user").filter(user_id=user_id).first()
    if not local or not local.stripe_subscription_id:
        messages.error(request, "This student does not have a Stripe annual subscription to verify.")
        return redirect(f"/subscription/manager/student-activity/?student={user_id}")

    dispute_id = (request.POST.get("stripe_dispute_id") or "").strip()
    if not dispute_id.startswith("du_"):
        messages.error(request, "Enter a valid Stripe dispute ID beginning with du_.")
        return redirect(f"/subscription/manager/student-activity/?student={user_id}")

    if local.dispute_external_id and local.dispute_external_id != dispute_id:
        messages.error(request, "A different Stripe dispute is already attached to this subscription. No changes were made.")
        return redirect(f"/subscription/manager/student-activity/?student={user_id}")

    try:
        dispute = stripe.Dispute.retrieve(
            dispute_id,
            api_key=stripe_subscription_views._subscription_api_key(),
        )
        remote, charge_id = stripe_subscription_views._stripe_subscription_from_dispute(dispute)
    except stripe.error.StripeError:
        messages.error(request, "Stripe could not verify that dispute right now. No access changes were made.")
        return redirect(f"/subscription/manager/student-activity/?student={user_id}")

    if remote is None or stripe_subscription_views._stripe_value(remote, "id") != local.stripe_subscription_id:
        messages.error(request, "That Stripe dispute does not belong to this student's PandaSpeak annual subscription. No changes were made.")
        return redirect(f"/subscription/manager/student-activity/?student={user_id}")

    status = stripe_subscription_views._stripe_value(dispute, "status", "open") or "open"
    if status in ("won", "warning_closed"):
        messages.info(request, "Stripe shows this dispute as resolved in PandaSpeak's favor, so access was not blocked.")
        return redirect(f"/subscription/manager/student-activity/?student={user_id}")

    local.is_disputed = True
    local.dispute_status = status
    local.dispute_provider = "stripe"
    local.dispute_external_id = dispute_id
    local.dispute_charge_id = charge_id or ""
    if not local.disputed_at:
        local.disputed_at = timezone.now()
    local.is_active = False
    local.plus_is_active = False
    local.save(update_fields=[
        "is_disputed",
        "dispute_status",
        "dispute_provider",
        "dispute_external_id",
        "dispute_charge_id",
        "disputed_at",
        "is_active",
        "plus_is_active",
    ])

    messages.success(
        request,
        f"Stripe dispute {dispute_id} was verified. {local.user.email} is now blocked from paid learning materials and activities while the dispute remains unresolved.",
    )
    return redirect(f"/subscription/manager/student-activity/?student={user_id}")
