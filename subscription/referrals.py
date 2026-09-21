from datetime import timedelta

from django.db import transaction
from django.utils import timezone

from .models import PlusReward, Referral, Subscription


REFERRAL_SESSION_KEY = "pandaspeak_referral_code"
FREE_PLUS_DAYS = 30


def remember_referral(request, code):
    """Remember a referral code until registration completes."""
    if code:
        request.session[REFERRAL_SESSION_KEY] = code.strip()[:32]


def attach_referral(user, code):
    """Attach a new student to a referrer once; never permit self-referral."""
    if not code or Referral.objects.filter(referred_user=user).exists():
        return None
    referrer_referral = Referral.objects.filter(code=code).select_related("referrer").first()
    if not referrer_referral or referrer_referral.referrer_id == user.id:
        return None
    return Referral.objects.create(referrer=referrer_referral.referrer, referred_user=user, code=code)


def referral_code_for(user):
    """Use one stable code for all referrals made by a student."""
    existing = Referral.objects.filter(referrer=user).values_list("code", flat=True).first()
    if existing:
        return existing
    # A seed row is intentionally not created; caller may display a code before
    # the first referral and pass it into registration. Use a deterministic,
    # non-sensitive token derived from the user's id.
    return f"ps{user.pk:x}invite"


def attach_referral_from_code(user, code):
    """Resolve either an existing referral code or the stable ps<id>invite form."""
    if not code or Referral.objects.filter(referred_user=user).exists():
        return None
    referrer = None
    existing = Referral.objects.filter(code=code).select_related("referrer").first()
    if existing:
        referrer = existing.referrer
    elif code.startswith("ps") and code.endswith("invite"):
        try:
            user_id = int(code[2:-6], 16)
            referrer = user.__class__.objects.filter(pk=user_id, is_active=True).first()
        except (TypeError, ValueError):
            pass
    if not referrer or referrer.pk == user.pk:
        return None
    return Referral.objects.create(referrer=referrer, referred_user=user, code=code)


@transaction.atomic
def grant_referral_rewards(referred_user):
    """Called only after the referred student's annual payment is confirmed."""
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


def promotional_plus_until(user):
    """Return promotional Plus expiry for earned months already activated."""
    sub = Subscription.objects.filter(user=user, is_active=True).first()
    return getattr(sub, "plus_promo_access_until", None) if sub else None


def available_reward_count(user):
    return PlusReward.objects.filter(user=user, status=PlusReward.STATUS_AVAILABLE).count()
