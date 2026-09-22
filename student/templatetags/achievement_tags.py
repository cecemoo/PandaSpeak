from django import template
from django.urls import reverse

from student.culture_views import CULTURE_PREVIEW_CARDS
from student.models import (
    AIConversationUsage,
    CulturalInsightCompletion,
    LearnedItem,
    PersonalFlashcard,
    StudentTestSubmission,
)
from subscription.models import PlusReward, Referral
from subscription.referrals import available_reward_count, referral_code_for

register = template.Library()

LEVEL2_LESSONS = {card['slug'] for card in CULTURE_PREVIEW_CARDS if card.get('level') == 'level2'}
LEVEL3_LESSONS = {card['slug'] for card in CULTURE_PREVIEW_CARDS if card.get('level') == 'level3'}


@register.inclusion_tag('student/_dashboard_achievements_and_referral.html', takes_context=True)
def my_achievements(context):
    """Build student achievements, next goal, and referral promotion data."""
    request = context.get('request')
    user = getattr(request, 'user', None)
    if not user or not user.is_authenticated:
        return {'achievements': [], 'earned_count': 0, 'total_count': 0, 'next_goal': None}

    completed = set(CulturalInsightCompletion.objects.filter(student=user).values_list('lesson_slug', flat=True))
    level2_count = len(completed & LEVEL2_LESSONS)
    level3_count = len(completed & LEVEL3_LESSONS)
    level2_total = len(LEVEL2_LESSONS)
    level3_total = len(LEVEL3_LESSONS)
    learned_count = LearnedItem.objects.filter(student=user).count()
    flashcard_count = PersonalFlashcard.objects.filter(student=user).count()
    test_count = StudentTestSubmission.objects.filter(student=user).count()
    ai_reply_count = AIConversationUsage.objects.filter(student=user, kind='reply').count()

    achievements = [
        {'icon':'🏮','name':'Culture Explorer','description':'Complete your first Cultural Insight.','earned':bool(completed),'progress':min(len(completed),1),'goal':1,'action_url':reverse('cultural_insights'),'action_label':'Explore Cultural Insights'},
        {'icon':'🐼🏮','name':'Level II Culture Enthusiast','description':f'Complete all {level2_total} Level II Cultural Insights.','earned':bool(level2_total) and level2_count==level2_total,'progress':level2_count,'goal':level2_total,'action_url':reverse('cultural_insights'),'action_label':'Continue Exploring'},
        {'icon':'🐼🌏','name':'Level III Culture Enthusiast','description':f'Complete all {level3_total} Level III Cultural Insights.','earned':bool(level3_total) and level3_count==level3_total,'progress':level3_count,'goal':level3_total,'action_url':reverse('cultural_insights'),'action_label':'Continue Exploring'},
        {'icon':'📚','name':'First Steps','description':'Learn your first PandaSpeak learning item.','earned':learned_count>=1,'progress':min(learned_count,1),'goal':1,'action_url':reverse('access_learning_materials'),'action_label':'Start Learning'},
        {'icon':'🌱','name':'Growing Learner','description':'Learn 25 vocabulary, sentence, or expression items.','earned':learned_count>=25,'progress':min(learned_count,25),'goal':25,'action_url':reverse('access_learning_materials'),'action_label':'Keep Learning'},
        {'icon':'⭐','name':'Dedicated Learner','description':'Learn 100 vocabulary, sentence, or expression items.','earned':learned_count>=100,'progress':min(learned_count,100),'goal':100,'action_url':reverse('access_learning_materials'),'action_label':'Keep Learning'},
        {'icon':'🈶','name':'Card Creator','description':'Create your first personal flash card.','earned':flashcard_count>=1,'progress':min(flashcard_count,1),'goal':1,'action_url':reverse('student_flashcards'),'action_label':'Create a Flash Card'},
        {'icon':'🤖','name':'Conversation Starter','description':'Practice your first AI Chinese conversation.','earned':ai_reply_count>=1,'progress':min(ai_reply_count,1),'goal':1,'action_url':reverse('ai_conversation'),'action_label':'Practice Conversation'},
        {'icon':'💬','name':'Conversation Explorer','description':'Exchange 25 replies while practicing with AI.','earned':ai_reply_count>=25,'progress':min(ai_reply_count,25),'goal':25,'action_url':reverse('ai_conversation'),'action_label':'Practice Conversation'},
        {'icon':'📋','name':'Test Taker','description':'Complete your first PandaSpeak test.','earned':test_count>=1,'progress':min(test_count,1),'goal':1,'action_url':reverse('test_list'),'action_label':'View Tests'},
        {'icon':'🏅','name':'Practice Pays Off','description':'Complete 5 PandaSpeak tests.','earned':test_count>=5,'progress':min(test_count,5),'goal':5,'action_url':reverse('test_list'),'action_label':'Take a Test'},
    ]

    unfinished = [a for a in achievements if not a['earned'] and a['goal']]
    next_goal = None
    if unfinished:
        next_goal = max(unfinished, key=lambda a: (a['progress'] / a['goal'], -a['goal']))
        remaining = max(next_goal['goal'] - next_goal['progress'], 0)
        next_goal = dict(next_goal)
        next_goal['remaining'] = remaining
        next_goal['percent'] = round((next_goal['progress'] / next_goal['goal']) * 100)
        next_goal['goal_text'] = (
            f"Just {remaining} more to unlock {next_goal['name']}!"
            if remaining == 1 else
            f"{remaining} more to unlock {next_goal['name']}."
        )

    referral_code = referral_code_for(user)
    referral_path = reverse('register') + f'?ref={referral_code}'
    referral_url = request.build_absolute_uri(referral_path)
    successful_referrals = Referral.objects.filter(referrer=user, rewarded_at__isnull=False).count()
    earned_rewards = PlusReward.objects.filter(user=user).count()
    queued_rewards = available_reward_count(user)

    return {
        'achievements': achievements,
        'earned_count': sum(1 for item in achievements if item['earned']),
        'total_count': len(achievements),
        'next_goal': next_goal,
        'show_referral_promotion': not getattr(user, 'is_teacher', False) and not user.is_staff,
        'referral_url': referral_url,
        'successful_referrals': successful_referrals,
        'referral_rewards_earned': earned_rewards,
        'referral_rewards_queued': queued_rewards,
    }
