from django.urls import path
from . import views


urlpatterns = [
    path('student_dashboard/', views.student_dashboard, name='student_dashboard'),
    path('access_learning_materials/', views.access_learning_materials, name='access_learning_materials'),
    path('subscription_plans/', views.subscription_plans, name='subscription_plans'),
    path('account_management_student/', views.account_management, name='account_management_student'),   

    path('vocabulary_page/', views.vocabulary_page, name='vocabulary_page'),
    path('sentence_page/', views.sentence_page, name='sentence_page'),  
    path('idiom_page/', views.idiom_page, name='idiom_page'),
]