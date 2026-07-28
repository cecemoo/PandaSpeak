from django.urls import path
from . import views



urlpatterns = [
    path('teacher_dashboard/', views.teacher_dashboard, name='teacher_dashboard'),
    path('account_management/', views.account_management, name='account_management'),  
    path('delete_account/', views.delete_account, name='delete_account'),

    path('add_vocabulary/', views.add_vocabulary, name='add_vocabulary'), 
    path('add_sentence/', views.add_sentence, name='add_sentence'),
    path('add_idiom/', views.add_idiom, name='add_idiom'),
    path('add_pronunciation/', views.add_pronunciation, name='add_pronunciation'),
    path('add_tone/', views.add_tone, name='add_tone'),

    path('teacher_course_bookings', views.teacher_course_bookings, name='teacher_course_bookings'),
    path('courses/<int:course_id>/delete/', views.delete_teacher_course, name='delete_teacher_course'),
    
]