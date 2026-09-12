from .models import Notification


NOTIFICATION_DISPLAY_LIMIT = 5


def notification_count(request):
    if request.user.is_authenticated:
        count = Notification.objects.filter(
            user=request.user,
            is_read=False
        ).count()
        count = min(count, NOTIFICATION_DISPLAY_LIMIT)
    else:
        count = 0
    return {
        'unread_notification_count': count
    }
