from django.urls import path
from . import views
from . import stripe_subscription_views
from . import subscription_guard_views


urlpatterns = [
    path('subscribe/', subscription_guard_views.guarded_subscribe, name='subscribe'),
    path('stripe/checkout/', subscription_guard_views.guarded_stripe_subscription_checkout, name='stripe_subscription_checkout'),
    path('stripe/success/', stripe_subscription_views.stripe_subscription_success, name='stripe_subscription_success'),
    path('stripe/webhook/', stripe_subscription_views.stripe_subscription_webhook, name='stripe_subscription_webhook'),
    path('checkout/<int:payment_id>/', views.create_tutoring_checkout_session, name='create_tutoring_checkout_session'),
    path('success/', views.subscription_success, name='subscription_success'),
    path('cancel/', views.cancel_subscription, name='cancel_subscription'),
]
