from django.urls import path
from . import views


urlpatterns = [
    path('checkout/<int:payment_id>/', views.create_tutoring_checkout_session, name='create_tutoring_checkout_session'),
    path('success/', views.subscription_success, name='subscription_success'),
    path('cancel/', views.cancel_subscription, name='cancel_subscription'),
]
