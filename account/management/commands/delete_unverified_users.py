from datetime import timedelta

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from account.models import CustomUser

# Hours a new account may stay unverified before it is treated as junk.
# Cece asked for unverified registrations to be removed automatically;
# 24 hours leaves room for a real student who registers at night and
# verifies the next morning. Change this one number to retune the window.
GRACE_HOURS = 24


def _related_record_count(user):
    total = 0
    for rel in user._meta.related_objects:
        try:
            related = getattr(user, rel.get_accessor_name())
        except Exception:
            continue
        if related is None:
            continue
        count = getattr(related, 'count', None)
        if callable(count):
            # ForeignKey / ManyToMany reverse manager.
            total += count()
        else:
            # OneToOne reverse relation: the object itself exists.
            total += 1
    return total


class Command(BaseCommand):
    help = ('Delete accounts that registered but never verified their email '
            'within the grace window and hold no data at all.')

    def handle(self, *args, **options):
        cutoff = timezone.now() - timedelta(hours=GRACE_HOURS)
        candidates = CustomUser.objects.filter(
            is_active=False,
            last_login__isnull=True,
            is_staff=False,
            is_superuser=False,
            is_teacher=False,
            date_joined__lte=cutoff,
        ).values_list('pk', flat=True)
        count = 0
        for pk in candidates.iterator():
            with transaction.atomic():
                user = CustomUser.objects.select_for_update().filter(
                    pk=pk,
                    is_active=False,
                    last_login__isnull=True,
                    is_staff=False,
                    is_superuser=False,
                    is_teacher=False,
                    date_joined__lte=cutoff,
                ).first()
                # Never delete an account that holds anything — a school
                # subscription, consent record, activity, payment, anything.
                if user is not None and _related_record_count(user) == 0:
                    user.delete()
                    count += 1
        self.stdout.write(f'Deleted {count} unverified account(s).')
