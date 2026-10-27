"""First-touch traffic attribution for lead-magnet signups (added 2026-10-27).

The lead pages stash the visitor's UTM source / referrer in the session on
the first GET; when the visitor submits the email form, the classified
source is stored on the LeadMagnetSignup so we can see whether signups
arrive from Facebook, Instagram, Threads, search, or elsewhere.
"""
from urllib.parse import urlparse

SESSION_KEY = "lead_attribution"

_HOST_SOURCES = (
    (("facebook.com", "fb.com"), "facebook"),
    (("instagram.com",), "instagram"),
    (("threads.net", "threads.com"), "threads"),
    (("google.",), "google"),
    (("bing.com",), "bing"),
    (("duckduckgo.com",), "duckduckgo"),
    (("yahoo.",), "yahoo"),
    (("pandaspeak.org",), "internal"),
)

_UTM_ALIASES = {
    "fb": "facebook",
    "facebook": "facebook",
    "ig": "instagram",
    "instagram": "instagram",
    "threads": "threads",
    "google": "google",
}


def _classify(host="", utm_source=""):
    utm = (utm_source or "").strip().lower()
    if utm:
        return _UTM_ALIASES.get(utm, utm[:64])
    host = (host or "").strip().lower()
    if not host:
        return "direct"
    for needles, label in _HOST_SOURCES:
        if any(needle in host for needle in needles):
            return label
    return host[:64]


def capture_lead_attribution(request):
    """Stash first-touch attribution in the session (GET lead pages)."""
    if SESSION_KEY in request.session:
        return
    referrer = request.META.get("HTTP_REFERER", "") or ""
    host = urlparse(referrer).netloc if referrer else ""
    request.session[SESSION_KEY] = {
        "utm_source": (request.GET.get("utm_source") or "")[:64],
        "referrer": referrer[:500],
        "host": host[:200],
    }


def attribution_for_signup(request):
    """Return the LeadMagnetSignup field values for this session's touch."""
    data = request.session.get(SESSION_KEY) or {}
    return {
        "traffic_source": _classify(data.get("host", ""), data.get("utm_source", "")),
        "referrer": (data.get("referrer") or "")[:500],
    }
