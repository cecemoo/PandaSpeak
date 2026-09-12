from django.conf import settings
from django.core import signing
from django.core.mail import EmailMessage
from django.core.management.base import BaseCommand
from django.urls import reverse
from account.models import AnnouncementDelivery, CustomUser


class Command(BaseCommand):
    help = 'Send up to 20 queued announcement emails; never retry uncertain deliveries automatically.'

    def handle(self, *args, **options):
        for delivery in AnnouncementDelivery.objects.filter(status='pending').select_related('announcement').order_by('pk')[:20]:
            # Atomic claim prevents overlapping workers from sending the same delivery.
            if not AnnouncementDelivery.objects.filter(pk=delivery.pk, status='pending').update(status='sending'):
                continue
            user = CustomUser.objects.filter(pk=delivery.user_id, is_active=True, news_emails=True).first()
            status = 'skipped'
            if user and user.email:
                token = signing.dumps(user.pk, salt='pandaspeak-news')
                link = 'https://pandaspeak.org' + reverse('news_unsubscribe', args=[token])
                body = (
                    'Dear PandaSpeak Users,\n\n'
                    "We'd like to share the following news and updates from PandaSpeak:\n\n"
                    + delivery.announcement.body
                    + '\n\nThank you for being part of the PandaSpeak community!\n\n'
                    'Best regards,\nThe PandaSpeak Team\n\n'
                    'You chose to receive PandaSpeak news and updates.\nUnsubscribe: ' + link
                )
                try:
                    sent = EmailMessage(delivery.announcement.subject, body, settings.DEFAULT_FROM_EMAIL, [user.email], reply_to=['pandaspeaksupport@gmail.com']).send(fail_silently=False)
                    status = 'sent' if sent else 'failed'
                except Exception:
                    status = 'failed'
            AnnouncementDelivery.objects.filter(pk=delivery.pk).update(status=status)
