import secrets

from django.conf import settings
from django.db import models


class Referral(models.Model):
    """One new student's referral relationship; a referred user can only count once."""

    referrer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="referrals_made",
    )
    referred_user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="referral_received",
    )
    code = models.CharField(max_length=32, db_index=True)
    rewarded_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.referrer} -> {self.referred_user}"


class PlusReward(models.Model):
    """A single free Plus month earned through a successful referral."""

    STATUS_AVAILABLE = "available"
    STATUS_APPLIED = "applied"
    STATUS_VOID = "void"
    STATUS_CHOICES = (
        (STATUS_AVAILABLE, "Available"),
        (STATUS_APPLIED, "Applied"),
        (STATUS_VOID, "Void"),
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="plus_rewards",
    )
    referral = models.ForeignKey(
        Referral,
        on_delete=models.CASCADE,
        related_name="plus_rewards",
    )
    status = models.CharField(max_length=12, choices=STATUS_CHOICES, default=STATUS_AVAILABLE)
    applied_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=("user", "referral"),
                name="unique_plus_reward_per_referral_user",
            )
        ]

    def __str__(self):
        return f"{self.user} - referral Plus month ({self.status})"


def new_referral_code():
    return secrets.token_urlsafe(8).replace("-", "").replace("_", "")[:12]
