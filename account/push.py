import json

from django.conf import settings

from pywebpush import webpush, WebPushException

from .models import PushSubscription

def send_push_to_user(user, title, body, url="/"):

    subscriptions = PushSubscription.objects.filter(user=user)

    payload = json.dumps({

        "title": title,

        "body": body,

        "url": url,

    })

    for subscription in subscriptions:

        subscription_info = {

            "endpoint": subscription.endpoint,

            "keys": {

                "p256dh": subscription.p256dh,

                "auth": subscription.auth,

            },

        }

        try:

            webpush(

                subscription_info=subscription_info,

                data=payload,

                vapid_private_key=settings.VAPID_PRIVATE_KEY_PATH,

                vapid_claims={

                    "sub": settings.VAPID_ADMIN_EMAIL

                },

            )

        except WebPushException as error:

            print("Push notification failed:", error)