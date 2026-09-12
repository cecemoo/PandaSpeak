from django.conf import settings
from django.db import models


class RescheduleRequest(models.Model):
    STATUS_CHOICES = (
        ("pending", "Pending"),
        ("accepted", "Accepted"),
        ("declined", "Declined"),
    )

    booking = models.OneToOneField(
        "course.Booking",
        on_delete=models.CASCADE,
        related_name="reschedule_request",
    )
    original_timeslot = models.ForeignKey(
        "course.TimeSlot",
        on_delete=models.PROTECT,
        related_name="reschedule_requests_from",
    )
    proposed_timeslot = models.ForeignKey(
        "course.TimeSlot",
        on_delete=models.PROTECT,
        related_name="reschedule_requests_to",
    )
    requested_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="tutoring_reschedule_requests_made",
    )
    requested_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="pending")
    responded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="tutoring_reschedule_requests_answered",
    )
    responded_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        ordering = ["-requested_at"]

    def __str__(self):
        return f"Reschedule booking {self.booking_id}: {self.status}"
