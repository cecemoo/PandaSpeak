import logging

from django.core.management.base import BaseCommand
from django.utils import timezone

from course.models import Booking
from course.payment_services import automatic_payouts_enabled, release_teacher_payment


logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Release eligible tutoring payments after the review window."

    def handle(self, *args, **options):
        if not automatic_payouts_enabled():
            self.stdout.write("Tutoring automatic payouts are disabled.")
            return

        booking_ids = list(
            Booking.objects.filter(
                status="confirmed",
                session_status="completed",
                payout_status="awaiting_release",
                student_reported_issue=False,
                is_refunded=False,
                stripe_transfer_id__isnull=True,
                payout_eligible_at__isnull=False,
                payout_eligible_at__lte=timezone.now(),
            ).values_list("id", flat=True)
        )

        released_count = 0
        for booking_id in booking_ids:
            try:
                released, reason = release_teacher_payment(booking_id)
                if released:
                    released_count += 1
                    self.stdout.write(
                        self.style.SUCCESS(
                            f"Released tutoring payout for booking {booking_id}: {reason}"
                        )
                    )
                else:
                    self.stdout.write(
                        f"Skipped booking {booking_id}: {reason}"
                    )
            except Exception as exc:
                logger.exception(
                    "Failed to release tutoring payout for booking %s",
                    booking_id,
                )
                self.stderr.write(
                    self.style.ERROR(
                        f"Booking {booking_id} payout failed: {exc}"
                    )
                )

        self.stdout.write(
            f"Tutoring payout scan complete. Released {released_count} of {len(booking_ids)} eligible booking(s)."
        )
