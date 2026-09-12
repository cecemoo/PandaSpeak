import logging
import os
from datetime import timedelta
from decimal import Decimal, ROUND_HALF_UP

import stripe
from django.conf import settings
from django.core.mail import send_mail
from django.db import transaction
from django.utils import timezone

from account.models import Notification
from .models import Booking


logger = logging.getLogger(__name__)
stripe.api_key = settings.STRIPE_SECRET_KEY


def automatic_payouts_enabled():
    return os.getenv(
        "TUTORING_AUTOMATIC_PAYOUTS_ENABLED",
        "false",
    ).lower() in {"1", "true", "yes", "on"}


def release_teacher_payment(booking_id):
    """Release one eligible tutoring payment to the teacher.

    This function is intentionally idempotent. It returns (released, reason).
    """
    if not automatic_payouts_enabled():
        return False, "automatic payouts disabled"

    with transaction.atomic():
        booking = (
            Booking.objects
            .select_for_update()
            .select_related("student", "timeslot__course__teacher", "timeslot__course")
            .get(pk=booking_id)
        )

        if booking.is_test_booking:
            return False, "test booking never releases Stripe funds"
        if booking.stripe_transfer_id or booking.payout_status == "transferred":
            return False, "already transferred"
        if booking.status != "confirmed":
            return False, "booking is not confirmed"
        if booking.is_refunded:
            return False, "booking was refunded"
        if booking.session_status != "completed":
            return False, "session is not completed"
        if booking.student_reported_issue or booking.payout_status == "on_hold":
            return False, "payout is on hold"
        if booking.payout_status != "awaiting_release":
            return False, "payout is not awaiting release"
        scheduled_review_end = booking.timeslot.end_time + timedelta(days=5)
        effective_eligible_at = max(
            filter(None, [booking.payout_eligible_at, scheduled_review_end])
        )
        if effective_eligible_at > timezone.now():
            return False, "review window has not ended"
        if not booking.stripe_payment_intent_id:
            return False, "missing Stripe PaymentIntent"

        teacher = booking.timeslot.course.teacher
        if not teacher.stripe_account_id:
            return False, "teacher has no connected Stripe account"

        commission_percent = Decimal(
            str(getattr(settings, "PANDASPEAK_COMMISSION_PERCENT", 20))
        )
        if commission_percent < 0 or commission_percent >= 100:
            raise ValueError("PANDASPEAK_COMMISSION_PERCENT must be between 0 and 100.")

        class_price = Decimal(str(booking.timeslot.course.price))
        teacher_amount = (
            class_price * (Decimal("100") - commission_percent) / Decimal("100")
        ).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        transfer_amount_cents = int(teacher_amount * Decimal("100"))

        if transfer_amount_cents <= 0:
            raise ValueError("Teacher payout amount must be positive.")

        payment_intent = stripe.PaymentIntent.retrieve(
            booking.stripe_payment_intent_id,
            expand=["latest_charge"],
        )
        latest_charge = getattr(payment_intent, "latest_charge", None)
        if isinstance(latest_charge, str):
            charge_id = latest_charge
        else:
            charge_id = getattr(latest_charge, "id", None) if latest_charge else None
        if not charge_id:
            raise ValueError("No Stripe charge was found for this booking.")

        metadata = getattr(payment_intent, "metadata", None)
        order_reference = (
            getattr(metadata, "order_reference", None)
            if metadata is not None
            else None
        ) or f"booking-{booking.pk}"

        transfer = stripe.Transfer.create(
            amount=transfer_amount_cents,
            currency="usd",
            destination=teacher.stripe_account_id,
            source_transaction=charge_id,
            transfer_group=order_reference,
            metadata={
                "booking_id": str(booking.pk),
                "timeslot_id": str(booking.timeslot_id),
                "teacher_id": str(teacher.pk),
                "student_id": str(booking.student_id),
                "payment_intent_id": booking.stripe_payment_intent_id,
                "teacher_amount": str(teacher_amount),
                "commission_percent": str(commission_percent),
                "release_reason": "completed_tutoring_session",
            },
            idempotency_key=f"booking-{booking.pk}-teacher-transfer",
        )

        booking.stripe_transfer_id = transfer.id
        booking.teacher_transfer_amount_cents = transfer_amount_cents
        booking.payout_status = "transferred"
        booking.payout_transferred_at = timezone.now()
        booking.save(update_fields=[
            "stripe_transfer_id",
            "teacher_transfer_amount_cents",
            "payout_status",
            "payout_transferred_at",
        ])

    Notification.objects.create(
        user=teacher,
        title="Tutoring Payment Released",
        message=(
            f"Payment for '{booking.timeslot.course.title}' has been released "
            "to your connected Stripe account."
        ),
        link="/course/teacher_bookings/",
    )
    Notification.objects.create(
        user=booking.student,
        title="Tutoring Session Completed",
        message=(
            f"The review period for '{booking.timeslot.course.title}' has ended "
            "and the teacher payment has been released."
        ),
        link="/course/my_bookings/",
    )

    if teacher.email:
        try:
            send_mail(
                "PandaSpeak Tutoring Payment Released",
                (
                    f"Dear {teacher.get_full_name()},\n\n"
                    f"Payment for '{booking.timeslot.course.title}' has been released "
                    "to your connected Stripe account.\n\n"
                    f"Amount: ${teacher_amount}\n\n"
                    "Best regards,\nPandaSpeak Support Team"
                ),
                settings.DEFAULT_FROM_EMAIL,
                [teacher.email],
                fail_silently=True,
            )
        except Exception:
            logger.exception("Teacher payout email failed for booking %s", booking.pk)

    logger.info(
        "Tutoring payout released. booking=%s transfer=%s amount_cents=%s",
        booking.pk,
        booking.stripe_transfer_id,
        booking.teacher_transfer_amount_cents,
    )
    return True, booking.stripe_transfer_id
