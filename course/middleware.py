from zoneinfo import ZoneInfo, ZoneInfoNotFoundError
from django.utils import timezone


class StudentTimezoneMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
    def __call__(self, request):
        timezone_name = request.session.get("student_timezone")
        if timezone_name:
            try:
                timezone.activate(ZoneInfo(timezone_name))
            except ZoneInfoNotFoundError:
                timezone.deactivate()
        else:
            timezone.deactivate()
        return self.get_response(request)