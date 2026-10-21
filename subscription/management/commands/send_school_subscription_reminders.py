from datetime import timedelta
from django.conf import settings
from django.core.mail import send_mail
from django.core.management.base import BaseCommand
from django.utils import timezone
from account.models import Notification
from subscription.models import Subscription
from subscription.school_models import SchoolEnrollment


class Command(BaseCommand):
    help = "Send school enrollment expiration notices 30, 7, and 1 days before expiration."

    def handle(self, *args, **kwargs):
        today = timezone.localdate()
        for days in (30, 7, 1):
            target = today + timedelta(days=days)
            enrollments = SchoolEnrollment.objects.select_related("student", "school").filter(
                expires_at__date=target, revoked_at__isnull=True, school__is_active=True,
            )
            for enrollment in enrollments:
                user = enrollment.student
                if not user.is_active or Subscription.objects.filter(user=user, is_disputed=True).exists():
                    continue
                title = f"PandaSpeak School Subscription: {days} Day Reminder"
                message = (
                    f"Your PandaSpeak Standard subscription through {enrollment.school.name} "
                    f"expires on {target:%B %d, %Y}. Please contact your school or PandaSpeak "
                    "to arrange renewal. Your Plus add-on, if any, is managed separately."
                )
                if Notification.objects.filter(user=user, title=title, created_at__date=today).exists():
                    continue
                Notification.objects.create(user=user, title=title, message=message, link="/student/account-management/")
                if user.email:
                    send_mail(title, message, settings.DEFAULT_FROM_EMAIL, [user.email], fail_silently=True)
        self.stdout.write(self.style.SUCCESS("School subscription reminders processed."))
