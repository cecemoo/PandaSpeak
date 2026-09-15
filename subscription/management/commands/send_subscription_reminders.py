from datetime import timedelta

from django.conf import settings
from django.core.mail import send_mail
from django.core.management.base import BaseCommand
from django.urls import reverse
from django.utils import timezone

from account.models import CustomUser, Notification
from account.push import send_push_to_user
from subscription.models import Subscription


class Command(BaseCommand):
    help = 'Send one reminder about PandaSpeak subscription renewal or expiring access.'

    def handle(self, *args, **options):
        today = timezone.localdate()
        target = today + timedelta(days=7)
        subscriptions = Subscription.objects.select_related('user').filter(access_until__date=target)

        for subscription in subscriptions:
            user = subscription.user
            if not user.is_active or user.is_teacher or user.is_staff:
                continue

            if subscription.is_active and not subscription.is_cancelled:
                title = 'PandaSpeak Subscription Renewal Reminder'
                message = f'Your PandaSpeak subscription is scheduled to renew on {target:%b %d, %Y}. It will renew automatically unless you cancel before then.'
                email_message = message + '\n\nTo cancel automatic renewal, sign in to PandaSpeak and open Subscription.'
            else:
                title = 'Continue Your PandaSpeak Subscription'
                message = f'Your PandaSpeak access ends on {target:%b %d, %Y}. Subscribe again to continue using subscriber learning materials.'
                email_message = message + '\n\nSign in to PandaSpeak to subscribe.'

            if Notification.objects.filter(user=user, title=title, created_at__date=today).exists():
                continue

            link = reverse('account_management_student')
            Notification.objects.create(user=user, title=title, message=message, link=link)
            send_push_to_user(user, title, message, link)
            if user.email:
                send_mail(title, email_message, settings.DEFAULT_FROM_EMAIL, [user.email], fail_silently=True)

        self.stdout.write(self.style.SUCCESS('Subscription reminders processed.'))
