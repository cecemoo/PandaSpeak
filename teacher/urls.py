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

    path('tests/create/', views.create_test, name='teacher_create_test'),
    path('tests/<int:test_id>/questions/', views.add_test_questions, name='teacher_add_test_questions'),
    path('tests/<int:test_id>/publish/', views.publish_test, name='publish_test'),
    path('teacher_test_list/', views.teacher_test_list, name='teacher_test_list'),
    path('tests/<int:test_id>/delete/', views.delete_test, name='teacher_delete_test'),
    path('tests/<int:test_id>/view/', views.teacher_view_test, name='teacher_view_test'),
    path('tests/results/', views.student_test_results, name='teacher_student_test_results'),
    path("surveys/create/", views.create_learning_survey, name="create_learning_survey"),
    path("surveys/<int:survey_id>/questions/add/", views.add_survey_question, name="add_survey_question"),
    path("surveys/<int:survey_id>/finish/", views.finish_learning_survey, name="finish_learning_survey"),
    path("surveys/", views.teacher_survey_list, name="teacher_survey_list"),
    path('surveys/<int:survey_id>/responses/', views.survey_responses, name='survey_responses'),
    
]