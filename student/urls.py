from django.urls import path
from . import views
from . import bingo_views
from . import flashcard_views
from . import subscription_guard_views
from . import tone_views
from . import challenge_views
from . import ai_conversation_views
from . import culture_views
from subscription.decorators import subscription_required


urlpatterns = [
    path('student_dashboard/', views.student_dashboard, name='student_dashboard'),
    path('subscription_plans/', subscription_guard_views.guarded_subscription_plans, name='subscription_plans'),
    path('account_management_student/', views.account_management, name='account_management_student'),
    path('subscription_locked/', views.subscription_locked, name='subscription_locked'),
    path('access_learning_materials/', subscription_required(views.access_learning_materials), name='access_learning_materials'),
    path('learning_material_search/', subscription_required(views.learning_material_search), name='learning_material_search'),
    path('vocabularies/category/<int:category_id>/', subscription_required(views.vocabulary_category_page), name='vocabulary_category_page'),
    path('sentences/category/<int:category_id>/', subscription_required(views.sentence_category_page), name='sentence_category_page'),
    path('idioms/category/<int:category_id>/', subscription_required(views.idiom_category_page), name='idiom_category_page'),
    path('pronunciations/', subscription_required(views.pronunciation_page), name='pronunciation_page'),
    path('pronunciations/next-tone-base/', subscription_required(tone_views.next_tone_base), name='next_tone_base'),
    path('cultural-insights/', subscription_required(culture_views.cultural_insights), name='cultural_insights'),
    path('cultural-insights/lesson/<slug:slug>/', subscription_required(culture_views.cultural_preview_detail), name='cultural_preview_detail'),
    path('cultural-insights/<int:pk>/', subscription_required(culture_views.cultural_insight_detail), name='cultural_insight_detail'),
    path('cultural-insights/<int:pk>/unlock/', subscription_required(culture_views.unlock_cultural_insight), name='unlock_cultural_insight'),
    path('flashcards/', subscription_required(flashcard_views.flashcards), name='student_flashcards'),
    path('flashcards/my-cards/', subscription_required(flashcard_views.manage_personal_flashcards), name='student_personal_flashcards'),
    path('flashcards/my-cards/<int:pk>/delete/', subscription_required(flashcard_views.delete_personal_flashcard), name='delete_personal_flashcard'),
    path('tests/', subscription_required(views.test_list), name='test_list'),
    path('tests/<int:test_id>/', subscription_required(views.take_test), name='take_test'),
    path('tests/question/<int:question_id>/submit-speaking/', subscription_required(views.submit_speaking_answer), name='submit_speaking_answer'),
    path('tests/results/<int:submission_id>/', subscription_required(views.test_result), name='test_result'),
    path('test-results/', subscription_required(views.student_test_results), name='student_test_results'),
    path('surveys/<int:survey_id>/take/', subscription_required(views.take_learning_survey), name='take_learning_survey'),
    path('surveys/', subscription_required(views.student_survey_list), name='student_survey_list'),
    path('bingo/', subscription_required(bingo_views.bingo_game_list), name='student_bingo_list'),
    path('bingo/<int:game_id>/play/', subscription_required(bingo_views.play_bingo), name='play_bingo'),
    path('chinese-challenge/', challenge_views.chinese_challenge, name='chinese_challenge'),
    path('chinese-challenge/question/', challenge_views.challenge_question, name='challenge_question'),
    path('ai-conversation/', ai_conversation_views.ai_conversation, name='ai_conversation'),
    path('ai-conversation/traditionalize/', ai_conversation_views.ai_conversation_traditionalize, name='ai_conversation_traditionalize'),
    path('ai-conversation/reply/', ai_conversation_views.ai_conversation_reply, name='ai_conversation_reply'),
    path('ai-conversation/speech/', ai_conversation_views.ai_conversation_speech, name='ai_conversation_speech'),
    path('learning-materials/change-level/', subscription_required(views.change_learning_level), name='change_learning_level'),
    path('favorites/toggle/<str:item_type>/<int:item_id>/', subscription_required(views.toggle_favorite), name='toggle_favorite'),
    path('my-review/', subscription_required(views.my_review), name='my_review'),
    path('learned/toggle/<str:item_type>/<int:item_id>/', subscription_required(views.toggle_learned), name='toggle_learned'),
    path('learned/', subscription_required(views.learned_items), name='learned_items'),
]
