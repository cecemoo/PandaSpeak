from .models import StudentActivity, Subscription


EXCLUDED_PREFIXES = (
    "/admin/",
    "/static/",
    "/media/",
    "/subscription/",
    "/accounts/",
)


class StudentActivityMiddleware:
    """Record authenticated student requests while paid learning access is active."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        user = getattr(request, "user", None)
        if not user or not user.is_authenticated:
            return response
        if user.is_staff or user.is_superuser or getattr(user, "is_teacher", False):
            return response
        if request.path.startswith(EXCLUDED_PREFIXES):
            return response
        if request.method not in ("GET", "POST"):
            return response
        if getattr(response, "status_code", 500) >= 500:
            return response

        subscription = Subscription.objects.filter(user=user, is_active=True, is_disputed=False).first()
        if not subscription:
            return response

        resolver_match = getattr(request, "resolver_match", None)
        forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR", "")
        ip_address = forwarded_for.split(",")[0].strip() if forwarded_for else request.META.get("REMOTE_ADDR")
        if ip_address and len(ip_address) > 45:
            ip_address = None

        StudentActivity.objects.create(
            user=user,
            activity_type="page_access",
            method=request.method,
            path=request.get_full_path()[:500],
            view_name=(getattr(resolver_match, "view_name", "") or "")[:200],
            ip_address=ip_address,
            user_agent=request.META.get("HTTP_USER_AGENT", "")[:2000],
            response_status=getattr(response, "status_code", None),
        )
        return response
