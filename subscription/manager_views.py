import stripe
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.mail import send_mail
from django.db.models import Count, Max, Q
from django.shortcuts import redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from account.models import Notification
from .models import StudentActivity, Subscription
from . import stripe_subscription_views


def _manager(user):
    return user.is_authenticated and (user.is_staff or user.is_superuser)


def _notify_dispute_suspension(local):
    student = local.user
    Notification.objects.create(
        user=student,
        title="PandaSpeak Access Suspended - Payment Dispute",
        message=(
            "A payment dispute has been reported for your PandaSpeak annual subscription. "
            "Your paid learning-material and activity access is suspended while the dispute remains open. "
            "If you did not intend to dispute this payment, please contact your bank or card issuer and ask them to withdraw the dispute. "
            "PandaSpeak will restore eligible access after Stripe confirms the dispute has been resolved in PandaSpeak's favor."
        ),
        link="/subscription/dispute-restricted/",
    )

    if student.email:
        greeting_name = student.first_name or student.get_full_name() or "Student"
        send_mail(
            subject="PandaSpeak Access Suspended - Payment Dispute",
            message=(
                f"Dear {greeting_name},\n\n"
                "We received notice through Stripe that a payment dispute has been opened for your PandaSpeak annual subscription. "
                "While the dispute is open, your access to PandaSpeak paid learning materials and activities has been suspended.\n\n"
                "If you did not intend to dispute this payment and would like your access restored, please contact your bank or card issuer and ask them to withdraw the dispute. "
                "PandaSpeak cannot restore access based only on a request from the cardholder; we must first receive confirmation through Stripe that the dispute has been resolved in PandaSpeak's favor. "
                "Once Stripe confirms that outcome and your subscription is otherwise eligible, PandaSpeak will restore your access automatically.\n\n"
                "If you have questions, please contact PandaSpeak Support at pandaspeaksupport@gmail.com.\n\n"
                "Best regards,\n"
                "PandaSpeak Team"
            ),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[student.email],
            fail_silently=True,
        )


def _subscription_from_dispute_checkout(dispute):
    """Verify a dispute through its Charge/PaymentIntent/Checkout Session.

    Older PandaSpeak subscriptions can keep the authoritative PandaSpeak user
    metadata on the Checkout Session rather than on the Subscription object.
    """
    api_key = stripe_subscription_views._subscription_api_key()
    charge_id = stripe_subscription_views._stripe_value(dispute, "charge")
    if not charge_id:
        return None, None

    charge = stripe.Charge.retrieve(charge_id, api_key=api_key)
    payment_intent_id = stripe_subscription_views._stripe_value(charge, "payment_intent")
    if not payment_intent_id:
        return None, charge_id

    sessions = stripe.checkout.Session.list(
        api_key=api_key,
        payment_intent=payment_intent_id,
        limit=10,
    )
    for session in sessions.auto_paging_iter():
        metadata = stripe_subscription_views._stripe_value(session, "metadata", {}) or {}
        if stripe_subscription_views._stripe_value(metadata, "purpose") != "pandaspeak_annual_subscription":
            continue
        sid = stripe_subscription_views._stripe_value(session, "subscription")
        if not sid:
            continue
        remote = stripe.Subscription.retrieve(sid, api_key=api_key)
        remote["metadata"] = metadata
        return remote, charge_id
    return None, charge_id


def _verified_subscription_from_dispute(dispute):
    # Prefer Checkout Session verification because that is where PandaSpeak's
    # purpose/user metadata lives for legacy annual subscriptions. The shared
    # subscription lookup remains a fallback for older invoice-based payments.
    remote, charge_id = _subscription_from_dispute_checkout(dispute)
    if remote is not None:
        return remote, charge_id
    return stripe_subscription_views._stripe_subscription_from_dispute(dispute)


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
    """Verify an existing Stripe dispute and attach it to the correct student."""
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
        remote, charge_id = _verified_subscription_from_dispute(dispute)
    except stripe.error.StripeError:
        messages.error(request, "Stripe could not verify that dispute right now. No access changes were made.")
        return redirect(f"/subscription/manager/student-activity/?student={user_id}")

    remote_sid = str(stripe_subscription_views._stripe_value(remote, "id") or "").strip()
    local_sid = str(local.stripe_subscription_id or "").strip()

    print("DISPUTE MANAGER DEBUG: remote_sid =", repr(remote_sid))
    print("DISPUTE MANAGER DEBUG: local_sid =", repr(local_sid))
    print("DISPUTE MANAGER DEBUG: match =", remote_sid == local_sid)

    if remote is None or remote_sid != local_sid:
        messages.error(request, "That Stripe dispute does not belong to this student's PandaSpeak annual subscription. No changes were made.")
        return redirect(f"/subscription/manager/student-activity/?student={user_id}")

    metadata = stripe_subscription_views._stripe_value(remote, "metadata", {}) or {}
    if str(stripe_subscription_views._stripe_value(metadata, "user_id", "")) != str(user_id):
        messages.error(request, "Stripe's PandaSpeak user metadata does not match this student. No changes were made.")
        return redirect(f"/subscription/manager/student-activity/?student={user_id}")

    status = stripe_subscription_views._stripe_value(dispute, "status", "open") or "open"
    if status in ("won", "warning_closed"):
        messages.info(request, "Stripe shows this dispute as resolved in PandaSpeak's favor, so access was not blocked.")
        return redirect(f"/subscription/manager/student-activity/?student={user_id}")

    newly_blocked = not local.is_disputed
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

    if newly_blocked:
        _notify_dispute_suspension(local)

    messages.success(
        request,
        f"Stripe dispute {dispute_id} was verified. {local.user.email} is now blocked from paid learning materials and activities while the dispute remains unresolved.",
    )
    return redirect(f"/subscription/manager/student-activity/?student={user_id}")
