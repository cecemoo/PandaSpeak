from django.urls import path
from . import announcement_views as views
urlpatterns = [
    path('preferences/', views.preferences, name='email_preferences'),
    path('unsubscribe/<str:token>/', views.unsubscribe, name='news_unsubscribe'),
    path('announcements/', views.compose, name='announcements'),
    path('announcements/<int:pk>/', views.preview, name='announcement_preview'),
    path('login/', views.preferences, name='my_login'),
]
