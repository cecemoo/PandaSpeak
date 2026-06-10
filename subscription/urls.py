from django.urls import path
from . import views



urlpatterns = [
    path('subscribe/', views.subscribe, name='subscribe'),
    path('checkout/', views.create_checkout_session, name='create_checkout_session'),
    path('success/', views.subscription_success, name='subscription_success'),
]