from django.urls import path
from . import views
from . import managers
from django.contrib.auth import views as auth_views


urlpatterns = [
    path('', views.home, name="home"),
    path('register/', views.register, name='register'),
    path('my_login/', views.my_login, name='my_login'),
    path('user_logout/', views.user_logout, name='user_logout'),

    path('password-reset/', auth_views.PasswordResetView.as_view(
        template_name='account/password_reset.html',
        email_template_name='account/password_reset_email.html',
        subject_template_name='account/password_reset_subject.txt'
    ), name='password_reset'),
    path('password-reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='account/password_reset_done.html'), name='password_reset_done'),
    path('password-reset-confirm/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='account/password_reset_confirm.html'), name='password_reset_confirm'),
    path('password-reset-complete/', auth_views.PasswordResetCompleteView.as_view(template_name='account/password_reset_complete.html'), name='password_reset_complete'),


    path('faq/', views.faq, name='faq'),
    path('terms/', views.terms, name='terms'),
    path('privacy/', views.privacy, name='privacy'),
    path('manager_dashboard/', views.manager_dashboard, name='manager_dashboard'),
    path('booking_management/', views.booking_management, name='booking_management'),
    path('booking/<int:booking_id>/refund/', views.refund_booking, name='refund_booking'),

    path('categories/', views.categories, name='categories'),
    path('add_vocab_category/', views.add_vocab_category, name='add_vocab_category'),
    path('add_sentence_category/', views.add_sentence_category, name='add_sentence_category'),
    path('add_idiom_category/', views.add_idiom_category, name='add_idiom_category'),

    path('vocab_category/<int:category_id>/edit/', views.edit_vocab_category, name='edit_vocab_category'),
    path('sentence_category/<int:category_id>/edit/', views.edit_sentence_category, name='edit_sentence_category'),
    path('idiom_category/<int:category_id>/edit/', views.edit_idiom_category, name='edit_idiom_category'),

    path('vocab_category/<int:category_id>/delete/', views.delete_vocab_category, name='delete_vocab_category'),
    path('sentence_category/<int:category_id>/delete/', views.delete_sentence_category, name='delete_sentence_category'),
    path('idiom_category/<int:category_id>/delete/', views.delete_idiom_category, name='delete_idiom_category'),

    path('vocabularies/', views.vocabularies, name='vocabularies'),
    path('vocabulary/<int:vocab_id>/edit/', views.edit_vocabulary, name='edit_vocabulary'),
    path('vocabulary/<int:vocab_id>/delete/', views.delete_vocabulary, name='delete_vocabulary'),

    path('sentences/', views.sentences, name='sentences'),
    path('sentence/<int:sentence_id>/edit/', views.edit_sentence, name='edit_sentence'),
    path('sentence/<int:sentence_id>/delete/', views.delete_sentence, name='delete_sentence'),

    path('idioms/', views.idioms, name='idioms'),
    path('idiom/<int:idiom_id>/edit/', views.edit_idiom, name='edit_idiom'),
    path('idiom/<int:idiom_id>/delete/', views.delete_idiom, name='delete_idiom'),

    path('pronunciations/', views.pronunciations, name='pronunciations'),
    path('pronunciation/<int:pronunciation_id>/edit/', views.edit_pronunciation, name='edit_pronunciation'),
    path('pronunciation/<int:pronunciation_id>/delete/', views.delete_pronunciation, name='delete_pronunciation'),

    path('tones/', views.tones, name='tones'),
    path('tone/<int:tone_id>/edit/', views.edit_tone, name='edit_tone'),
    path('tone/<int:tone_id>/delete/', views.delete_tone, name='delete_tone'),

    path('lessons/', views.lessons, name='lessons'),
    # path('lesson/<int:lesson_id>/edit/', views.edit_lesson, name='edit_lesson'),
    path('lesson/<int:lesson_id>/delete/', views.delete_lesson, name='delete_lesson'),

    path('placement-questions/', 
        views.manage_placement_questions,
        name='manage_placement_questions'
    ),
    path('placement-questions/add/',
        views.add_placement_question,
        name='add_placement_question'
    ),
    path('placement-test/', views.placement_test, name='placement_test'),

    path('notifications/', views.notifications, name='notifications'),
    path('notifications/<int:notification_id>/read/', views.mark_notification_read, name='mark_notification_read'),

    path('push/subscribe/', views.save_push_subscription, name='save_push_subscription'),
    path('service-worker.js', views.service_worker, name='service_worker'),

]