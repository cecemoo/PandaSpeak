"""Central PandaSpeak subscription feature policy."""

from django.utils import timezone

STANDARD_PLAN = "standard"
PLUS_PLAN = "plus"
STANDARD_AI_CONVERSATIONS = 10
PLUS_AI_CONVERSATIONS = 50


def _subscription(user):
    try:
        return user.subscription
    except Exception:
        return None


def has_base_access(user):
    sub = _subscription(user)
    if not sub or not sub.is_active:
        return False
    return not sub.access_until or sub.access_until > timezone.now()


def is_plus(user):
    """Plus can come from paid access or an earned promotional month."""
    sub = _subscription(user)
    if not sub or not has_base_access(user):
        return False
    now = timezone.now()
    paid = sub.plus_is_active and (not sub.plus_access_until or sub.plus_access_until > now)
    promo = bool(sub.plus_promo_access_until and sub.plus_promo_access_until > now)
    return paid or promo


def subscription_tier(user):
    return PLUS_PLAN if is_plus(user) else STANDARD_PLAN


def ai_conversation_limit(user):
    return PLUS_AI_CONVERSATIONS if is_plus(user) else STANDARD_AI_CONVERSATIONS


def student_level_number(user):
    for attr in ("learning_level", "level", "student_level"):
        value = getattr(user, attr, None)
        if value:
            text = str(value).lower()
            if "3" in text or "iii" in text:
                return 3
            if "2" in text or "ii" in text:
                return 2
    return 1


def history_access(user):
    level = student_level_number(user)
    plus = is_plus(user)
    return {
        "allowed": plus and level >= 2,
        "is_plus": plus,
        "level": level,
        "requires_plus": not plus,
        "requires_level2": level < 2,
        "reason": "available" if plus and level >= 2 else "level" if plus and level < 2 else "plus_and_level" if level < 2 else "plus",
    }


def plan_features(user):
    tier = subscription_tier(user)
    return {
        "tier": tier,
        "display_name": "PandaSpeak Plus" if tier == PLUS_PLAN else "PandaSpeak Standard",
        "is_plus": tier == PLUS_PLAN,
        "ai_conversation_limit": ai_conversation_limit(user),
        "history": history_access(user),
    }
