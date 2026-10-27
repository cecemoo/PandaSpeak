"""Token-protected internal trigger for the daily lead-follow-up drip.

Cece chose Option 1 on 2026-10-26: instead of a Render cron, a scheduled
job on Muse's side POSTs here once a day. The endpoint stays inert
(503) until LEAD_FOLLOWUP_TOKEN is set in the service environment, and
every call must present that token as a Bearer credential.
"""
import hmac
import io

from django.conf import settings
from django.core.management import call_command
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST


@csrf_exempt
@require_POST
def lead_followups_trigger(request):
    expected = getattr(settings, "LEAD_FOLLOWUP_TOKEN", "") or ""
    if not expected:
        return JsonResponse({"ok": False, "error": "not_configured"}, status=503)
    auth = request.headers.get("Authorization", "")
    provided = auth[len("Bearer "):] if auth.startswith("Bearer ") else ""
    if not provided or not hmac.compare_digest(provided, expected):
        return JsonResponse({"ok": False, "error": "unauthorized"}, status=401)
    out = io.StringIO()
    call_command("send_lead_followups", stdout=out)
    return JsonResponse({"ok": True, "output": out.getvalue().strip()})
