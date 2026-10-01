from django.shortcuts import redirect

from .models import StudentActivity, Subscription


EXCLUDED_PREFIXES = (
    "/admin/",
    "/static/",
    "/media/",
    "/subscription/",
    "/accounts/",
)


class StudentActivityMiddleware:
    """Block disputed students from student routes and record permitted activity."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        user = getattr(request, "user", None)

        # Defense in depth: once a payment dispute is recorded, a normal student
        # must not reach any /student/ material or activity route, even if a future
        # view is accidentally added without @subscription_required.
        if (
            user
            and user.is_authenticated
            and not user.is_staff
            and not user.is_superuser
            and not getattr(user, "is_teacher", False)
            and request.path.startswith("/student/")
            and Subscription.objects.filter(user=user, is_disputed=True).exists()
        ):
            return redirect("dispute_restricted")

        response = self.get_response(request)

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
