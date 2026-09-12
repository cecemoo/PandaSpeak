from datetime import timedelta
from decimal import Decimal, ROUND_HALF_UP

import stripe
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.http import require_POST

from account.models import Notification
from account.push import send_push_to_user
from .models import Booking, TimeSlot
from .reschedule_models import RescheduleRequest


stripe.api_key = settings.STRIPE_SECRET_KEY


def _is_party(booking, user):
    return (
        booking.student_id == user.id
        or booking.timeslot.course.teacher_id == user.id
    )


def _other_party(booking, user):
    if booking.student_id == user.id:
        return booking.timeslot.course.teacher
    return booking.student


def _booking_page_for(user):
    return "course:teacher_bookings" if getattr(user, "is_teacher", False) else "course:my_bookings"


def _notify(user, title, message, link):
    Notification.objects.create(
        user=user,
        title=title,
        message=message,
        link=link,
    )
    send_push_to_user(user, title, message, link)


@login_required(login_url="my_login")
def request_reschedule(request, pk):
    booking = get_object_or_404(
        Booking.objects.select_related(
            "student", "timeslot", "timeslot__course", "timeslot__course__teacher"
        ),
        pk=pk,
    )
    if not _is_party(booking, request.user):
        messages.error(request, "You do not have permission to reschedule this booking.")
        return redirect("home")

    cutoff = timezone.now() + timedelta(hours=24)
    if (
        booking.status != "confirmed"
        or booking.session_status != "scheduled"
        or booking.timeslot.start_time <= cutoff
    ):
        messages.error(
            request,
            "Rescheduling is available only more than 24 hours before the scheduled session.",
        )
        return redirect(_booking_page_for(request.user))

    course = booking.timeslot.course
    candidate_slots = list(
        TimeSlot.objects.filter(
            course=course,
            start_time__gt=cutoff,
        )
        .exclude(pk=booking.timeslot_id)
        .order_by("start_time")
    )
    available_slots = [slot for slot in candidate_slots if slot.is_available]

    if request.method == "POST":
        proposed_id = request.POST.get("timeslot_id")
        proposed = get_object_or_404(TimeSlot, pk=proposed_id, course=course)
        if proposed.start_time <= cutoff:
            messages.error(request, "Please choose a session time that is more than 24 hours away.")
            return redirect("course:request_reschedule", pk=booking.pk)
        if proposed.pk == booking.timeslot_id or not proposed.is_available:
            messages.error(request, "That time slot is no longer available. Please choose another time.")
            return redirect("course:request_reschedule", pk=booking.pk)

        reschedule_request, _ = RescheduleRequest.objects.update_or_create(
            booking=booking,
            defaults={
                "original_timeslot": booking.timeslot,
                "proposed_timeslot": proposed,
                "requested_by": request.user,
                "status": "pending",
                "responded_by": None,
                "responded_at": None,
            },
        )

        other = _other_party(booking, request.user)
        link = reverse(_booking_page_for(other))
        requester_name = request.user.get_full_name() or request.user.email
        message = (
            f"{requester_name} requested to move '{course.title}' from "
            f"{booking.timeslot.start_time:%b %d, %Y %I:%M %p} to "
            f"{proposed.start_time:%b %d, %Y %I:%M %p}."
        )
        _notify(other, "Tutoring Reschedule Requested", message, link)
        messages.success(
            request,
            "Reschedule request sent. The original session remains booked until the other party accepts.",
        )
        return redirect(_booking_page_for(request.user))

    return render(
        request,
        "course/request_reschedule.html",
        {
            "booking": booking,
            "available_slots": available_slots,
        },
    )


@login_required(login_url="my_login")
@require_POST
def respond_reschedule(request, pk, decision):
    if decision not in {"accept", "decline"}:
        messages.error(request, "Invalid reschedule response.")
        return redirect("home")

    with transaction.atomic():
        rr = get_object_or_404(
            RescheduleRequest.objects.select_for_update().select_related(
                "booking",
                "booking__student",
                "booking__timeslot",
                "booking__timeslot__course",
                "booking__timeslot__course__teacher",
                "proposed_timeslot",
                "requested_by",
            ),
            booking_id=pk,
        )
        booking = rr.booking

        if not _is_party(booking, request.user) or rr.requested_by_id == request.user.id:
            messages.error(request, "Only the other party can respond to this reschedule request.")
            return redirect(_booking_page_for(request.user))
        if rr.status != "pending":
            messages.info(request, "This reschedule request has already been answered.")
            return redirect(_booking_page_for(request.user))
        if booking.status != "confirmed" or booking.timeslot.start_time <= timezone.now():
            messages.error(request, "This booking can no longer be rescheduled.")
            return redirect(_booking_page_for(request.user))

        rr.responded_by = request.user
        rr.responded_at = timezone.now()

        if decision == "decline":
            rr.status = "declined"
            rr.save(update_fields=["status", "responded_by", "responded_at"])
            requester = rr.requested_by
            link = reverse(_booking_page_for(requester))
            _notify(
                requester,
                "Tutoring Reschedule Declined",
                "Your tutoring reschedule request was declined. You may request another time if the session is still more than 24 hours away, or cancel the booking.",
                link,
            )
            messages.success(request, "Reschedule request declined. The original booking remains unchanged.")
            return redirect(_booking_page_for(request.user))

        proposed = TimeSlot.objects.select_for_update().get(pk=rr.proposed_timeslot_id)
        confirmed_count = proposed.bookings.filter(status="confirmed").count()
        if confirmed_count >= proposed.capacity:
            messages.error(request, "The proposed time slot is no longer available.")
            return redirect(_booking_page_for(request.user))

        old_slot = booking.timeslot
        booking.timeslot = proposed
        booking.session_status = "scheduled"
        booking.reminder_24h_sent_at = None
        booking.reminder_1h_sent_at = None
        booking.save(
            update_fields=[
                "timeslot",
                "session_status",
                "reminder_24h_sent_at",
                "reminder_1h_sent_at",
            ]
        )
        rr.status = "accepted"
        rr.save(update_fields=["status", "responded_by", "responded_at"])

        requester = rr.requested_by
        title = "Tutoring Reschedule Accepted"
        msg = (
            f"Your tutoring session was moved from {old_slot.start_time:%b %d, %Y %I:%M %p} "
            f"to {proposed.start_time:%b %d, %Y %I:%M %p}."
        )
        _notify(requester, title, msg, reverse(_booking_page_for(requester)))
        _notify(request.user, title, msg, reverse(_booking_page_for(request.user)))
        messages.success(request, "Reschedule accepted. The booking has been moved to the new time.")
        return redirect(_booking_page_for(request.user))


@login_required(login_url="my_login")
@require_POST
def cancel_after_declined_reschedule(request, pk):
    booking = get_object_or_404(
        Booking.objects.select_related(
            "student", "timeslot", "timeslot__course", "timeslot__course__teacher"
        ),
        pk=pk,
    )
    rr = get_object_or_404(RescheduleRequest, booking=booking)

    if rr.status != "declined" or rr.requested_by_id != request.user.id:
        messages.error(request, "This cancellation option is available only to the party whose reschedule request was declined.")
        return redirect(_booking_page_for(request.user))
    if booking.status != "confirmed" or booking.timeslot.start_time <= timezone.now():
        messages.error(request, "This booking can no longer be canceled through the reschedule workflow.")
        return redirect(_booking_page_for(request.user))

    try:
        if booking.stripe_payment_intent_id and not booking.is_refunded and not booking.is_test_booking:
            price = Decimal(str(booking.timeslot.course.price))
            refund_amount_cents = int(price * Decimal("100"))
            commission_percent = Decimal(
                str(getattr(settings, "PANDASPEAK_COMMISSION_PERCENT", 20))
            )
            teacher_amount_cents = int(
                (
                    price
                    * (Decimal("100") - commission_percent)
                    / Decimal("100")
                ).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
                * Decimal("100")
            )
            refund = stripe.Refund.create(
                payment_intent=booking.stripe_payment_intent_id,
                amount=refund_amount_cents,
                reason="requested_by_customer",
                metadata={
                    "booking_id": str(booking.pk),
                    "reason": "reschedule_declined",
                },
                idempotency_key=f"booking-refund-{booking.pk}",
            )
            if booking.stripe_transfer_id:
                stripe.Transfer.create_reversal(
                    booking.stripe_transfer_id,
                    amount=teacher_amount_cents,
                    metadata={
                        "booking_id": str(booking.pk),
                        "refund_id": refund.id,
                        "reason": "reschedule_declined_cancel",
                    },
                    idempotency_key=f"booking-transfer-reversal-{booking.pk}",
                )
            booking.is_refunded = True
            booking.save(update_fields=["is_refunded"])
    except stripe.error.StripeError as exc:
        messages.error(request, f"Refund failed: {exc}. Please contact PandaSpeak Support.")
        return redirect(_booking_page_for(request.user))

    student = booking.student
    teacher = booking.timeslot.course.teacher
    booking.cancel()

    for user in (student, teacher):
        _notify(
            user,
            "Tutoring Booking Canceled",
            "The tutoring booking was canceled after a reschedule request was declined.",
            reverse(_booking_page_for(user)),
        )

    if student.email:
        send_mail(
            "Your PandaSpeak Tutoring Booking Was Canceled",
            "Your tutoring booking was canceled after the reschedule request was declined. If payment was collected, the applicable refund has been initiated.",
            settings.DEFAULT_FROM_EMAIL,
            [student.email],
            fail_silently=True,
        )
    if teacher.email:
        send_mail(
            "A PandaSpeak Tutoring Booking Was Canceled",
            "A tutoring booking was canceled after a reschedule request was declined.",
            settings.DEFAULT_FROM_EMAIL,
            [teacher.email],
            fail_silently=True,
        )

    messages.success(request, "Booking canceled. Any applicable refund has been initiated.")
    return redirect(_booking_page_for(request.user))
