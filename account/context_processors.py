from .models import Notification


NOTIFICATION_DISPLAY_LIMIT = 5


def notification_count(request):
    if request.user.is_authenticated:
        recent_notifications = Notification.objects.filter(
            user=request.user
        ).order_by('-created_at')[:NOTIFICATION_DISPLAY_LIMIT]
        count = sum(1 for notification in recent_notifications if not notification.is_read)
    else:
        count = 0
    return {
        'unread_notification_count': count
    }
