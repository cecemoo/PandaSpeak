from datetime import timedelta

from django.db import transaction
from django.utils import timezone

from .models import PlusReward, Referral, Subscription


REFERRAL_SESSION_KEY = "pandaspeak_referral_code"
FREE_PLUS_DAYS = 30


def remember_referral(request, code):
    if code:
        request.session[REFERRAL_SESSION_KEY] = code.strip()[:32]


def referral_code_for(user):
    # Stable without storing a second profile/token table.
    return f"ps{user.pk:x}invite"


def attach_referral_from_code(user, code):
    """Attach a new student once. Self-referrals and invalid codes are ignored."""
    if not code or Referral.objects.filter(referred_user=user).exists():
        return None
    if not (code.startswith("ps") and code.endswith("invite")):
        return None
    try:
        referrer_id = int(code[2:-6], 16)
    except (TypeError, ValueError):
        return None
    referrer = user.__class__.objects.filter(pk=referrer_id, is_active=True).first()
    if not referrer or referrer.pk == user.pk or getattr(referrer, "is_teacher", False) or referrer.is_staff:
        return None
    return Referral.objects.create(referrer=referrer, referred_user=user, code=code)


@transaction.atomic
def grant_referral_rewards(referred_user):
    """Grant exactly once, after a referred student's annual payment is confirmed."""
    referral = Referral.objects.select_for_update().filter(
        referred_user=referred_user,
        rewarded_at__isnull=True,
    ).first()
    if not referral:
        return False
    PlusReward.objects.get_or_create(user=referral.referrer, referral=referral)
    PlusReward.objects.get_or_create(user=referral.referred_user, referral=referral)
    referral.rewarded_at = timezone.now()
    referral.save(update_fields=["rewarded_at"])
    return True


@transaction.atomic
def activate_next_free_month(user):
    """Activate one earned month for a Standard student.

    Paid Plus subscribers keep rewards queued; their reward must be consumed by
    Stripe billing rather than extending a local date while Stripe still bills.
    """
    sub = Subscription.objects.select_for_update().filter(user=user, is_active=True).first()
    if not sub or sub.plus_is_active:
        return False
    reward = PlusReward.objects.select_for_update().filter(
        user=user,
        status=PlusReward.STATUS_AVAILABLE,
    ).order_by("created_at").first()
    if not reward:
        return False
    now = timezone.now()
    start = max(now, sub.plus_promo_access_until or now)
    sub.plus_promo_access_until = start + timedelta(days=FREE_PLUS_DAYS)
    sub.save(update_fields=["plus_promo_access_until"])
    reward.status = PlusReward.STATUS_APPLIED
    reward.applied_at = now
    reward.save(update_fields=["status", "applied_at"])
    return True


def available_reward_count(user):
    return PlusReward.objects.filter(user=user, status=PlusReward.STATUS_AVAILABLE).count()
