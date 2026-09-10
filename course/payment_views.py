import logging

import stripe
from django.conf import settings
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

from .views import create_paid_bookings_from_session


logger = logging.getLogger(__name__)
stripe.api_key = settings.STRIPE_SECRET_KEY


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
