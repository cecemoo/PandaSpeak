import logging

import stripe
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

from account.models import Notification
from .views import create_paid_bookings_from_session, format_class_time, get_teacher_timezone


logger = logging.getLogger(__name__)
stripe.api_key = settings.STRIPE_SECRET_KEY


def _notify_managers_of_tutoring_booking(student, booking):
    """Send one internal notification and email per manager for a paid booking.

    Notification.get_or_create makes Stripe webhook retries safe: resending the
    same checkout event will not create duplicate manager emails/notifications.
    """
    slot = booking.timeslot
    course = slot.course
    teacher = course.teacher
    teacher_timezone_name, teacher_tz = get_teacher_timezone(course)
    session_time = format_class_time(slot.start_time, slot.end_time, teacher_tz)

    student_name = student.get_full_name() or student.email
    teacher_name = teacher.get_full_name() or teacher.email
    amount = course.price
    title = "New Tutoring Session Booked"
    message = (
        f"Booking #{booking.pk}: {student_name} booked '{course.title}' "
        f"with {teacher_name} for {session_time} ({teacher_timezone_name}). "
        f"Amount: ${amount}."
    )

    User = get_user_model()
    managers = User.objects.filter(is_staff=True, is_active=True)

    for manager in managers:
        notification, created = Notification.objects.get_or_create(
            user=manager,
            title=title,
            message=message,
            defaults={"link": None},
        )

        if not created or not manager.email:
            continue

        try:
            send_mail(
                "PandaSpeak - New Tutoring Session Booked",
                (
                    f"Dear {manager.get_full_name() or 'PandaSpeak Manager'},\n\n"
                    "A paid tutoring session has been booked.\n\n"
                    f"Booking ID: {booking.pk}\n"
                    f"Student: {student_name}\n"
                    f"Student Email: {student.email}\n"
                    f"Teacher: {teacher_name}\n"
                    f"Teacher Email: {teacher.email}\n"
                    f"Course: {course.title}\n"
                    f"Time: {session_time}\n"
                    f"Time Zone: {teacher_timezone_name}\n"
                    f"Amount: ${amount}\n\n"
                    "Best regards,\n"
                    "PandaSpeak Support Team"
                ),
                settings.DEFAULT_FROM_EMAIL,
                [manager.email],
                fail_silently=False,
            )
        except Exception:
            # The booking is already paid and saved. An email failure must not
            # make Stripe retry the booking event or duplicate the booking.
            logger.exception(
                "Manager tutoring-booking email failed. Manager=%s booking=%s",
                manager.pk,
                booking.pk,
            )


@csrf_exempt
def stripe_webhook(request):
    """Stripe webhook for tutoring checkout.

    Checkout confirms paid bookings only. Teacher transfers are intentionally
    deferred until the tutoring session is completed and the review window ends.
    """
    if request.method != "POST":
        return HttpResponse(status=405)

    payload = request.body
    signature = request.META.get("HTTP_STRIPE_SIGNATURE")
    if not signature:
        return HttpResponse(status=400)

    try:
        event = stripe.Webhook.construct_event(
            payload=payload,
            sig_header=signature,
            secret=settings.STRIPE_WEBHOOK_SECRET,
        )
    except ValueError:
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError:
        return HttpResponse(status=400)

    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        session_id = getattr(session, "id", None)
        payment_status = getattr(session, "payment_status", None)
        mode = getattr(session, "mode", None)

        # This endpoint creates tutoring bookings only. Subscription Checkout
        # sessions are handled by the subscription payment flow.
        if mode != "payment":
            logger.info(
                "Ignoring non-tutoring Checkout session: session=%s mode=%s",
                session_id,
                mode,
            )
            return HttpResponse(status=200)

        logger.info(
            "Checkout completed: session=%s payment_status=%s",
            session_id,
            payment_status,
        )

        if payment_status == "paid":
            try:
                student, bookings, _ = create_paid_bookings_from_session(session)
                for booking in bookings:
                    # A paid booking begins in payout=pending. Session attendance
                    # will move it to awaiting_release only after completion.
                    if not booking.stripe_transfer_id and booking.payout_status != "transferred":
                        booking.payout_status = "pending"
                        booking.save(update_fields=["payout_status"])

                    _notify_managers_of_tutoring_booking(student, booking)

                logger.info(
                    "Paid tutoring bookings confirmed without teacher transfer. "
                    "session=%s student=%s bookings=%s",
                    session_id,
                    student.pk,
                    [booking.pk for booking in bookings],
                )
            except Exception:
                logger.exception(
                    "Failed to create paid bookings for Stripe session %s",
                    session_id,
                )
                return HttpResponse(status=500)

    return HttpResponse(status=200)
