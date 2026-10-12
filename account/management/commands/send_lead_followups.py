"""Daily drip emails for lead-magnet signups.

Source-aware: 'bopomofo-chart' signups get the BoPoMoFo sequence;
'idioms' signups get the idioms sequence.
Day 2: study tip.
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


IDIOMS_DAY2_SUBJECT = 'Idiom of the day: 雪中送炭 — help that arrives just in time'
IDIOMS_DAY2_BODY = (
    'Hi there,\n\n'
    'Here is a study tip that works with your Everyday Chinese Idioms PDF: learn one idiom a day, '
    'out loud, inside a sentence about your own life. Idioms stick when they are attached to a real moment.\n\n'
    'Try today\'s: 雪中送炭 (xuě zhōng sòng tàn, ㄒㄩㄝˇ ㄓㄨㄥˉ ㄙㄨㄥˋ ㄊㄢˋ) — literally "sending '
    'charcoal in the snow." It means giving someone help exactly when they need it most. Example: '
    '他在我最難的時候幫我，真是雪中送炭。("He helped me when things were hardest — truly charcoal in the snow.")\n\n'
    'All 36 idioms from the PDF are also online with the same format — Traditional characters, '
    'BoPoMoFo, Pinyin, and example sentences:\n'
    'https://pandaspeak.org/learn-chinese-idioms/\n\n'
    'Happy learning!\nThe PandaSpeak Team'
)

IDIOMS_DAY5_SUBJECT = 'Ready to go beyond the idioms?'
IDIOMS_DAY5_BODY = (
    'Hi there,\n\n'
    'You have 36 everyday idioms in your pocket — now comes the fun part: the vocabulary, sentences, '
    'and stories that let you use them naturally. Here is the fastest path:\n\n'
    '1. Take the free placement test (2 minutes) to find your level:\n'
    '   https://pandaspeak.org/placement-test/\n'
    '2. Explore 24/7 learning materials matched to you — vocabulary, pronunciation, idioms, Chinese '
    'history journeys, games, and AI conversation practice.\n'
    '3. Book a live online tutoring session when you want a real teacher (we handle the time zones).\n\n'
    'Start here: https://pandaspeak.org/learn-traditional-chinese-online/\n\n'
    'Happy learning!\nThe PandaSpeak Team'
)


def _day2_for(signup):
    if signup.source == 'idioms':
        return IDIOMS_DAY2_SUBJECT, IDIOMS_DAY2_BODY
    return DAY2_SUBJECT, DAY2_BODY


def _day5_for(signup):
    if signup.source == 'idioms':
        return IDIOMS_DAY5_SUBJECT, IDIOMS_DAY5_BODY
    return DAY5_SUBJECT, DAY5_BODY


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
                subject, body = _day2_for(s)
                _send_lead_email(s, subject, body)
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
                subject, body = _day5_for(s)
                _send_lead_email(s, subject, body)
                sent += 1
            except Exception as e:
                self.stderr.write(f'day5 failed for {s.email}: {e}')

        self.stdout.write(f'sent {sent} lead follow-up emails')
