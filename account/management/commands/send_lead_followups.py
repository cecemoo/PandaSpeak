"""Daily drip emails for lead-magnet signups.

Day 2: study tip + pronunciation tables nudge.
Day 5: placement test / Plus / tutoring nudge.
Run once daily (e.g. Render cron job). Never retries uncertain deliveries.
"""
from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from account.models import LeadMagnetSignup
from account.views import _send_lead_email


DAY2_SUBJECT = 'Quick BoPoMoFo tip: learn them in groups'
DAY2_BODY = (
    'Hi there,\n\n'
    'A quick tip for your BoPoMoFo chart: learn the initials in mouth-shape groups instead of '
    'one by one — ㄅㄆㄇㄈ (lips), ㄉㄊㄋㄌ (tongue tip), ㄍㄎㄏ (throat). Saying each group out loud '
    'locks the sounds in much faster.\n\n'
    'Want to hear every symbol pronounced? Our BoPoMoFo and Pinyin tables have audio for each one, '
    'and every lesson comes with listen-along audio in standard Mandarin:\n'
    'https://pandaspeak.org/bopomofo-for-adults/\n\n'
    'Happy learning!\nThe PandaSpeak Team'
)

DAY5_SUBJECT = 'Ready to go beyond the chart?'
DAY5_BODY = (
    'Hi there,\n\n'
    'Your BoPoMoFo chart covers the sounds — now comes the fun part: real words, sentences, and '
    'stories. Here is the fastest path:\n\n'
    '1. Take the free placement test (2 minutes) to find your level:\n'
    '   https://pandaspeak.org/placement-test/\n'
    '2. Explore 24/7 learning materials matched to you — vocabulary, pronunciation, Chinese history '
    'journeys, games, and AI conversation practice.\n'
    '3. Book a live online tutoring session when you want a real teacher (we handle the time zones).\n\n'
    'Start here: https://pandaspeak.org/learn-traditional-chinese-online/\n\n'
    'Happy learning!\nThe PandaSpeak Team'
)


class Command(BaseCommand):
    help = 'Send day-2 and day-5 follow-up emails to lead magnet signups.'

    def handle(self, *args, **options):
        now = timezone.now()
        sent = 0

        day2_cutoff = now - timedelta(days=2)
        for s in LeadMagnetSignup.objects.filter(
                unsubscribed=False, followup_day2_sent=False,
                created_at__lte=day2_cutoff):
            if not LeadMagnetSignup.objects.filter(pk=s.pk, followup_day2_sent=False).update(followup_day2_sent=True):
                continue
            try:
                _send_lead_email(s, DAY2_SUBJECT, DAY2_BODY)
                sent += 1
            except Exception as e:
                self.stderr.write(f'day2 failed for {s.email}: {e}')

        day5_cutoff = now - timedelta(days=5)
        for s in LeadMagnetSignup.objects.filter(
                unsubscribed=False, followup_day5_sent=False,
                created_at__lte=day5_cutoff):
            if not LeadMagnetSignup.objects.filter(pk=s.pk, followup_day5_sent=False).update(followup_day5_sent=True):
                continue
            try:
                _send_lead_email(s, DAY5_SUBJECT, DAY5_BODY)
                sent += 1
            except Exception as e:
                self.stderr.write(f'day5 failed for {s.email}: {e}')

        self.stdout.write(f'sent {sent} lead follow-up emails')
