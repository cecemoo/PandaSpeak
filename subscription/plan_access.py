"""Central PandaSpeak subscription feature policy.

This module intentionally does not change Stripe/PayPal billing yet. It gives the
application one place to decide what Standard and Plus users can access before
we wire a second checkout product.
"""

STANDARD_PLAN = "standard"
PLUS_PLAN = "plus"

STANDARD_AI_CONVERSATIONS = 10
PLUS_AI_CONVERSATIONS = 50


def _plan_text(user):
    """Return normalized plan text from the user's active Subscription."""
    try:
        subscription = user.subscription
    except Exception:
        return ""
    if not subscription or not subscription.is_active or subscription.is_cancelled:
        return ""
    return str(subscription.subscription_plan or "").strip().lower()


def subscription_tier(user):
    """Map current and future billing plan names to Standard or Plus."""
    text = _plan_text(user)
    if "plus" in text or "premium" in text or "upgrade" in text:
        return PLUS_PLAN
    return STANDARD_PLAN


def is_plus(user):
    return subscription_tier(user) == PLUS_PLAN


def ai_conversation_limit(user):
    """Conversation allowance for the subscription cycle.

    Standard keeps the existing included allowance; Plus receives 50.
    The usage-reset/billing-cycle implementation will be wired with Plus billing.
    """
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
    """Describe Chinese History Journey access without leaking premium content."""
    level = student_level_number(user)
    plus = is_plus(user)
    return {
        "allowed": plus and level >= 2,
        "is_plus": plus,
        "level": level,
        "requires_plus": not plus,
        "requires_level2": level < 2,
        "reason": (
            "available"
            if plus and level >= 2
            else "level"
            if plus and level < 2
            else "plus_and_level"
            if level < 2
            else "plus"
        ),
    }


def plan_features(user):
    """Convenient feature bundle for templates/views."""
    tier = subscription_tier(user)
    return {
        "tier": tier,
        "display_name": "PandaSpeak Plus" if tier == PLUS_PLAN else "PandaSpeak Standard",
        "is_plus": tier == PLUS_PLAN,
        "ai_conversation_limit": ai_conversation_limit(user),
        "history": history_access(user),
    }
