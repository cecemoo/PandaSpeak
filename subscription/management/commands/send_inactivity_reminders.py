"""Email students who have not logged in for over 5 days.

Runs daily from the EC2 crontab (installed by the deploy workflow).
A student gets at most one reminder per inactivity spell: once a
reminder has gone out, no other is sent until the student logs in
again and then stays away for another 5+ days. The reminder recaps
the last items the student studied and their overall progress, and
is also left as a site Notification (which doubles as the record
that throttles repeat sends) plus a web push.
"""

from datetime import timedelta

from django.conf import settings
from django.core.mail import send_mail
from django.core.management.base import BaseCommand
from django.urls import reverse
from django.utils import timezone

from account.models import CustomUser, Notification
from account.push import send_push_to_user
from student.models import LearnedItem
from student.study_reminder import (
    _idiom_label,
    _progress_counts,
    _sentence_label,
    _vocab_label,
)

INACTIVITY_DAYS = 5
REMINDER_TITLE = '👋 We Miss You at PandaSpeak!'
MAX_RECENT_ITEMS = 5


def _item_label(item):
    if item.vocabulary_id:
        return _vocab_label(item)
    if item.sentence_id:
        return _sentence_label(item)
    return _idiom_label(item)


class Command(BaseCommand):
    help = (
        'Email students who have not logged in for over '
        f'{INACTIVITY_DAYS} days, once per inactivity spell.'
    )

    def handle(self, *args, **options):
        now = timezone.now()
        cutoff = now - timedelta(days=INACTIVITY_DAYS)
        students = CustomUser.objects.filter(
            is_active=True,
            is_staff=False,
            is_superuser=False,
            is_teacher=False,
            last_login__isnull=False,
            last_login__lt=cutoff,
        ).exclude(email='')

        sent = 0
        for user in students:
            last_reminder = (
                Notification.objects.filter(user=user, title=REMINDER_TITLE)
                .order_by('-created_at').first()
            )
            if last_reminder is not None and (
                last_reminder.created_at >= user.last_login
            ):
                # Already reminded during this inactivity spell.
                continue

            recent_items = list(
                LearnedItem.objects.filter(student=user)
                .select_related('vocabulary', 'sentence', 'idiom')
                .order_by('-learned_at')[:MAX_RECENT_ITEMS]
            )
            progress = _progress_counts(user)

            lines = [
                "It's been a little while since your last visit to "
                'PandaSpeak — your Chinese misses you!',
            ]
            if recent_items:
                lines += ['', 'Last time you studied:']
                lines += [f'• {_item_label(item)}' for item in recent_items]
            if progress['total_learned'] > 0:
                lines += [
                    '',
                    'Your overall progress so far: '
                    f"{progress['total_learned']} of "
                    f"{progress['total_materials']} materials learned "
                    f"({progress['overall_progress']}%) — "
                    f"{progress['learned_vocabulary']} words · "
                    f"{progress['learned_sentences']} sentences · "
                    f"{progress['learned_expressions']} expressions.",
                ]
            lines += [
                '',
                'Pick up right where you left off — sign in to continue '
                'learning: https://pandaspeak.org/my_login/',
            ]
            message = '\n'.join(lines)

            link = reverse('student_dashboard')
            Notification.objects.create(
                user=user, title=REMINDER_TITLE, message=message, link=link)
            try:
                send_push_to_user(user, REMINDER_TITLE, message, link)
            except Exception:
                pass
            greeting = (
                f'Hello {user.first_name or "PandaSpeak learner"},\n\n'
            )
            footer = (
                '\n\nBest regards,\nPandaSpeak Team\n'
                'Learn Chinese. Speak with Confidence.\n'
                'https://pandaspeak.org'
            )
            send_mail(
                REMINDER_TITLE, greeting + message + footer,
                settings.DEFAULT_FROM_EMAIL, [user.email],
                fail_silently=True,
            )
            sent += 1

        self.stdout.write(
            f'Inactivity reminders sent: {sent} '
            f'(inactive over {INACTIVITY_DAYS} days)'
        )
