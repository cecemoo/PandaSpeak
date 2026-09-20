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
    help = 'Send PandaSpeak subscription renewal, expiration, and occasional subscription reminders.'

    def handle(self, *args, **options):
        today = timezone.localdate()
        target = today + timedelta(days=7)
        subscriptions = Subscription.objects.select_related('user').filter(access_until__date=target)

        for subscription in subscriptions:
            user = subscription.user
            if not user.is_active or user.is_teacher or user.is_staff:
                continue

            plus_active = subscription.plus_is_active and (not subscription.plus_access_until or subscription.plus_access_until > timezone.now())
            if subscription.is_active and not subscription.is_cancelled:
                title = 'PandaSpeak Subscription Renewal Reminder'
                message = f'Your $15 annual PandaSpeak subscription is scheduled to renew on {target:%b %d, %Y}. It will renew automatically unless you cancel before then.'
                if not plus_active:
                    message += ' PandaSpeak Plus is also available as an optional $4.99/month add-on for expanded AI Conversation Practice and Plus features.'
                email_message = message + '\n\nTo manage annual renewal or PandaSpeak Plus, sign in to PandaSpeak and open Subscription.'
            else:
                title = 'Continue Your PandaSpeak Subscription'
                message = f'Your PandaSpeak annual access ends on {target:%b %d, %Y}. Subscribe again to continue using subscriber learning materials.'
                if not plus_active:
                    message += ' After your annual membership is active, you can also add PandaSpeak Plus for expanded AI Conversation Practice.'
                email_message = message + '\n\nSign in to PandaSpeak to manage your subscription.'

            if Notification.objects.filter(user=user, title=title, created_at__date=today).exists():
                continue

            link = reverse('account_management_student')
            Notification.objects.create(user=user, title=title, message=message, link=link)
            send_push_to_user(user, title, message, link)
            if user.email:
                greeting = f'Hello {user.first_name or "PandaSpeak learner"},\n\n'
                footer = '\n\nBest regards,\nPandaSpeak Team\nLearn Chinese. Speak with Confidence.\nhttps://pandaspeak.org'
                send_mail(title, greeting + email_message + footer, settings.DEFAULT_FROM_EMAIL, [user.email], fail_silently=True)

        # Plus has its own monthly cycle. Remind students seven days before that
        # paid period ends/renews without affecting the annual membership.
        plus_subscriptions = Subscription.objects.select_related('user').filter(plus_is_active=True, plus_access_until__date=target)
        for subscription in plus_subscriptions:
            user = subscription.user
            if not user.is_active or user.is_teacher or user.is_staff:
                continue
            if subscription.plus_is_cancelled:
                title = 'PandaSpeak Plus Ends Soon'
                message = f'Your paid PandaSpeak Plus access ends on {target:%b %d, %Y}. There is no refund for the current month. After that date you will return to PandaSpeak Standard; your $15 annual subscription remains separate and active according to its own renewal status.'
            else:
                title = 'PandaSpeak Plus Renewal Reminder'
                message = f'Your PandaSpeak Plus add-on is scheduled to renew on {target:%b %d, %Y} at $4.99/month. Canceling Plus stops the next Plus renewal but does not cancel your $15 annual PandaSpeak subscription.'
            if Notification.objects.filter(user=user, title=title, created_at__date=today).exists():
                continue
            link = reverse('account_management_student')
            Notification.objects.create(user=user, title=title, message=message, link=link)
            send_push_to_user(user, title, message, link)
            if user.email:
                email_message = f'Hello {user.first_name or "PandaSpeak learner"},\n\n{message}\n\nSign in to PandaSpeak and open Subscription to manage your plans.\n\nBest regards,\nPandaSpeak Team\nLearn Chinese. Speak with Confidence.\nhttps://pandaspeak.org'
                send_mail(title, email_message, settings.DEFAULT_FROM_EMAIL, [user.email], fail_silently=True)

        if today.day == 1:
            title = 'Continue Learning with PandaSpeak'
            message = 'Subscribe to PandaSpeak to continue using subscriber Chinese learning materials and activities.'
            link = reverse('account_management_student')
            students = CustomUser.objects.filter(is_active=True,is_teacher=False,is_staff=False,news_emails=True).exclude(subscription__is_active=True,subscription__is_cancelled=False).distinct()
            for user in students:
                if Notification.objects.filter(user=user,title=title,created_at__year=today.year,created_at__month=today.month).exists():
                    continue
                Notification.objects.create(user=user,title=title,message=message,link=link)
                send_push_to_user(user,title,message,link)
                if user.email:
                    email_message=(f'Hello {user.first_name or "PandaSpeak learner"},\n\n{message}\n\nSign in to PandaSpeak and open Subscription to subscribe.\n\nBest regards,\nPandaSpeak Team\nLearn Chinese. Speak with Confidence.\nhttps://pandaspeak.org')
                    send_mail(title,email_message,settings.DEFAULT_FROM_EMAIL,[user.email],fail_silently=True)

        self.stdout.write(self.style.SUCCESS('Subscription reminders processed.'))
