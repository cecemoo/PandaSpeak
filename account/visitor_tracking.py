"""Counts unique daily website visitors for the manager dashboard.

One DailyVisitor row per visitor per day. A visitor is identified by a
SHA-256 hash of IP + user agent (the raw IP is never stored). Counting
rules:
- only successful (200) GET requests that return HTML pages
- staff/superuser browsing is not counted (it's not visitor traffic)
- obvious bots/crawlers and tool user agents are not counted
- repeat page views by the same visitor on the same day count once

A cache flag per visitor/day keeps the database write to at most one
per visitor per day, and any failure in counting is swallowed so it can
never break a page.
"""
import hashlib
import logging

from django.core.cache import cache
from django.urls import reverse
from django.utils import timezone

from .models import DailyVisitor, VisitorAction

logger = logging.getLogger(__name__)

_BOT_MARKERS = (
    'bot', 'crawler', 'spider', 'slurp', 'curl', 'wget',
    'python-requests', 'headless', 'mediapartners',
)
_EXCLUDED_PREFIXES = (
    '/static/', '/media/', '/internal/', '/help-chat/',
    '/challenge/', '/favicon',
)


def _client_ip(request):
    forwarded = request.META.get('HTTP_X_FORWARDED_FOR', '')
    if forwarded:
        return forwarded.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR', 'unknown')


def visitor_key_for(request):
    user_agent = request.META.get('HTTP_USER_AGENT', '')
    return hashlib.sha256(
        ('%s|%s' % (_client_ip(request), user_agent)).encode('utf-8')
    ).hexdigest()


def _is_countable(request):
    """Staff/superuser browsing and obvious bots are not visitor traffic."""
    user = getattr(request, 'user', None)
    if user is not None and user.is_authenticated and (
            user.is_staff or user.is_superuser):
        return False
    lowered = request.META.get('HTTP_USER_AGENT', '').lower()
    return not any(marker in lowered for marker in _BOT_MARKERS)


def record_action(request, action):
    """Record that this visitor performed `action` today (once per day).

    Used by the Panda assistant and 60-Second Challenge endpoints; the
    register page view is recorded by the middleware below. Never raises.
    """
    try:
        if not _is_countable(request):
            return
        VisitorAction.objects.get_or_create(
            visitor_key=visitor_key_for(request),
            action=action,
            date=timezone.localdate(),
        )
    except Exception:
        logger.exception('Visitor action tracking failed')


class VisitorTrackingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        try:
            self._record(request, response)
        except Exception:
            logger.exception('Visitor tracking failed')
        return response

    def _record(self, request, response):
        if request.method != 'GET' or response.status_code != 200:
            return
        if request.path.startswith(_EXCLUDED_PREFIXES):
            return
        if 'text/html' not in response.get('Content-Type', ''):
            return
        if not _is_countable(request):
            return
        visitor_key = visitor_key_for(request)
        today = timezone.localdate()
        if request.path == reverse('register'):
            VisitorAction.objects.get_or_create(
                visitor_key=visitor_key, action='register_view', date=today)
        if request.path == reverse('about'):
            VisitorAction.objects.get_or_create(
                visitor_key=visitor_key, action='about_view', date=today)
        if request.path == reverse('course:course_list'):
            VisitorAction.objects.get_or_create(
                visitor_key=visitor_key, action='tutoring_view', date=today)
        match = getattr(request, 'resolver_match', None)
        if (match is not None and match.namespace == 'course'
                and match.url_name == 'course_detail'):
            VisitorAction.objects.get_or_create(
                visitor_key=visitor_key, action='course_detail_view',
                date=today)
        cache_key = 'visitor_counted:%s:%s' % (visitor_key, today.isoformat())
        if cache.get(cache_key):
            return
        DailyVisitor.objects.get_or_create(visitor_key=visitor_key, date=today)
        cache.set(cache_key, 1, 60 * 60 * 26)
