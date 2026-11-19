"""Password-reset confirm view that also lifts the login throttle.

A user who was paused by the brute-force throttle (too many failed
attempts) can still reset their password by email at any time — the
reset pages are never throttled. Once the reset succeeds, the account's
failure counter is cleared so they can sign in immediately with the
new password instead of waiting out the rest of the pause.
"""
from django.contrib.auth import views as auth_views

from . import login_throttle


class PasswordResetConfirmView(auth_views.PasswordResetConfirmView):
    def form_valid(self, form):
        response = super().form_valid(form)
        if self.user is not None:
            login_throttle.record_success(self.request, self.user.get_username())
        return response
