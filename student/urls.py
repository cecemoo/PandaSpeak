from django.urls import path
from . import views


urlpatterns = [
    path('student_dashboard/', views.student_dashboard, name='student_dashboard'),
    path('access_learning_materials/', views.access_learning_materials, name='access_learning_materials'),
    path('subscription_plans/', views.subscription_plans, name='subscription_plans'),
    path('account_management_student/', views.account_management, name='account_management_student'), 
    path('subscription_locked/', views.subscription_locked, name='subscription_locked'),  

    path('vocabularies/category/<int:category_id>/', views.vocabulary_category_page, name='vocabulary_category_page'),
    path('sentences/category/<int:category_id>/', views.sentence_category_page, name='sentence_category_page'),
    path('idioms/category/<int:category_id>/', views.idiom_category_page, name='idiom_category_page'),
    path('pronunciations/', views.pronunciation_page, name='pronunciation_page'),

    
]