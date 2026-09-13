from django.urls import path
from . import views
from . import stripe_subscription_views


urlpatterns = [
    path('subscribe/', views.subscribe, name='subscribe'),
    path('stripe/checkout/', stripe_subscription_views.stripe_subscription_checkout, name='stripe_subscription_checkout'),
    path('stripe/webhook/', stripe_subscription_views.stripe_subscription_webhook, name='stripe_subscription_webhook'),
    path('checkout/<int:payment_id>/', views.create_tutoring_checkout_session, name='create_tutoring_checkout_session'),
    path('success/', views.subscription_success, name='subscription_success'),
    path('cancel/', views.cancel_subscription, name='cancel_subscription'),
]
