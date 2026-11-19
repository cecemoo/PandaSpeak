"""Brute-force protection for the login page (added 2026-11-19).

Failed login attempts are counted in the Django cache per account and
per source IP. Once a limit is hit, further attempts are refused until
the window passes — this blunts password guessing and credential
stuffing without locking the real owner out for long.

Limits (15-minute windows):
- per account (email): 5 failures
- per IP address:     20 failures (shared IPs / offices get more room)

A successful login clears the account counter (the IP counter decays
on its own). Blocked attempts are logged so abuse is visible in the
server log.
"""
import logging

from django.core.cache import cache

logger = logging.getLogger(__name__)

WINDOW_SECONDS = 15 * 60
ACCOUNT_LIMIT = 5
IP_LIMIT = 20


def _client_ip(request):
    forwarded = request.META.get('HTTP_X_FORWARDED_FOR', '')
    if forwarded:
        return forwarded.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR', 'unknown')


def _account_key(username):
    return 'login_fail_acct:%s' % (username or '').strip().lower()


def _ip_key(request):
    return 'login_fail_ip:%s' % _client_ip(request)


def is_blocked(request, username):
    """True when this account or this IP has too many recent failures."""
    if cache.get(_account_key(username), 0) >= ACCOUNT_LIMIT:
        return True
    if cache.get(_ip_key(request), 0) >= IP_LIMIT:
        return True
    return False


def record_failure(request, username):
    for key in (_account_key(username), _ip_key(request)):
        try:
            cache.incr(key)
        except ValueError:
            cache.set(key, 1, WINDOW_SECONDS)
    if is_blocked(request, username):
        logger.warning(
            'Login throttled: account=%s ip=%s reached the failure limit',
            (username or '').strip().lower(), _client_ip(request),
        )


def record_success(request, username):
    cache.delete(_account_key(username))
