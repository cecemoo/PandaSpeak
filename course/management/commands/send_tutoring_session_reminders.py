import logging
from datetime import timedelta
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from django.conf import settings
from django.core.mail import send_mail
from django.core.management.base import BaseCommand
from django.db import transaction
from django.urls import reverse
from django.utils import timezone

from account.models import Notification
from account.push import send_push_to_user
from course.models import Booking


logger = logging.getLogger(__name__)
REMINDER_WINDOW = timedelta(minutes=1)


class Command(BaseCommand):
    help = "Send 24-hour and 1-hour tutoring session reminders to students and teachers."

    def handle(self, *args, **options):
        now = timezone.now()
        sent_24h = self._send_due_reminders(
            now=now,
            offset=timedelta(hours=24),
            sent_field="reminder_24h_sent_at",
            label="24 hours",
            short_label="24-hour",
        )
        sent_1h = self._send_due_reminders(
            now=now,
            offset=timedelta(hours=1),
            sent_field="reminder_1h_sent_at",
            label="1 hour",
            short_label="1-hour",
        )

        self.stdout.write(
            self.style.SUCCESS(
                f"Tutoring reminder scan complete. Sent {sent_24h} 24-hour and {sent_1h} 1-hour reminder(s)."
            )
        )

    def _send_due_reminders(self, *, now, offset, sent_field, label, short_label):
        target = now + offset
        booking_ids = list(
            Booking.objects.filter(
                status="confirmed",
                is_refunded=False,
                session_status="scheduled",
                timeslot__start_time__gte=target - REMINDER_WINDOW,
                timeslot__start_time__lte=target + REMINDER_WINDOW,
                **{f"{sent_field}__isnull": True},
            ).values_list("id", flat=True)
        )

        sent_count = 0
        for booking_id in booking_ids:
            try:
                with transaction.atomic():
                    booking = (
                        Booking.objects.select_for_update()
                        .select_related(
                            "student",
                            "timeslot__course",
                            "timeslot__course__teacher",
                        )
                        .get(pk=booking_id)
                    )

                    if getattr(booking, sent_field):
                        continue
                    if booking.status != "confirmed" or booking.is_refunded:
                        continue
                    if booking.session_status != "scheduled":
                        continue

                    start_time = booking.timeslot.start_time
                    lower = target - REMINDER_WINDOW
                    upper = target + REMINDER_WINDOW
                    if not (lower <= start_time <= upper):
                        continue

                    self._notify_participants(
                        booking=booking,
                        label=label,
                        short_label=short_label,
                    )
                    setattr(booking, sent_field, timezone.now())
                    booking.save(update_fields=[sent_field])
                    sent_count += 1

            except Exception as exc:
                logger.exception(
                    "Failed to send %s tutoring reminder for booking %s",
                    short_label,
                    booking_id,
                )
                self.stderr.write(
                    self.style.ERROR(
                        f"Booking {booking_id} {short_label} reminder failed: {exc}"
                    )
                )

        return sent_count

    def _notify_participants(self, *, booking, label, short_label):
        course = booking.timeslot.course
        teacher = course.teacher
        student = booking.student
        session_path = reverse("course:tutoring_session", args=[booking.pk])
        site_base_url = getattr(settings, "SITE_BASE_URL", "https://pandaspeak.org").rstrip("/")
        session_url = f"{site_base_url}{session_path}"
        display_time = self._format_session_time(booking)

        participants = (
            (student, teacher, "student"),
            (teacher, student, "teacher"),
        )

        for recipient, other_person, role in participants:
            recipient_name = recipient.get_full_name() or recipient.email
            other_name = other_person.get_full_name() or other_person.email
            title = f"PandaSpeak Tutoring Session in {label}"

            if role == "student":
                body = (
                    f"Your tutoring session with {other_name} starts in {label}. "
                    f"Session time: {display_time}."
                )
                email_role_line = f"Teacher: {other_name}"
            else:
                body = (
                    f"Your tutoring session with {other_name} starts in {label}. "
                    f"Session time: {display_time}."
                )
                email_role_line = f"Student: {other_name}"

            Notification.objects.get_or_create(
                user=recipient,
                title=f"{title} #{booking.pk}",
                link=session_path,
                defaults={"message": body},
            )

            send_push_to_user(
                recipient,
                title,
                body,
                session_path,
            )

            if recipient.email:
                send_mail(
                    subject=f"PandaSpeak {short_label.title()} Tutoring Session Reminder",
                    message=(
                        f"Hi {recipient_name},\n\n"
                        f"This is a reminder that your PandaSpeak tutoring session starts in {label}.\n\n"
                        f"{email_role_line}\n"
                        f"Session time: {display_time}\n\n"
                        f"Open your tutoring session:\n{session_url}\n\n"
                        "You will be able to enter the classroom when the session join window opens.\n\n"
                        "PandaSpeak"
                    ),
                    from_email=getattr(settings, "DEFAULT_FROM_EMAIL", None),
                    recipient_list=[recipient.email],
                    fail_silently=True,
                )

    def _format_session_time(self, booking):
        course = booking.timeslot.course
        timezone_name = course.teacher_timezone or "America/Chicago"
        try:
            tz = ZoneInfo(timezone_name)
        except ZoneInfoNotFoundError:
            tz = timezone.get_current_timezone()
            timezone_name = str(tz)

        local_start = timezone.localtime(booking.timeslot.start_time, tz)
        return f"{local_start.strftime('%A, %B %d, %Y at %I:%M %p')} ({timezone_name})"
