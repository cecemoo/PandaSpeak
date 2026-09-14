from django.apps import AppConfig


class SubscriptionConfig(AppConfig):
    name = 'subscription'

    def ready(self):
        # Register subscription lifecycle signals (manager notifications, etc.).
        from . import signals  # noqa: F401
