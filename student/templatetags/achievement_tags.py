from django import template

from student.models import (
    AIConversationUsage,
    CulturalInsightCompletion,
    LearnedItem,
    PersonalFlashcard,
    StudentTestSubmission,
)

register = template.Library()

LEVEL2_LESSONS = {
    'red-envelopes',
    'dining-etiquette',
    'tea-culture',
    'gift-giving',
    'lucky-numbers',
    'family-address',
}

LEVEL3_LESSONS = {
    'historical-influences',
    'regional-differences',
    'festivals-today',
    'workplace-etiquette',
    'indirect-communication',
    'modern-society',
}


@register.inclusion_tag('student/_my_achievements.html', takes_context=True)
def my_achievements(context):
    """Build student achievements from activity already tracked by PandaSpeak."""
    request = context.get('request')
    user = getattr(request, 'user', None)
    if not user or not user.is_authenticated:
        return {'achievements': [], 'earned_count': 0, 'total_count': 0}

    completed = set(
        CulturalInsightCompletion.objects.filter(student=user).values_list(
            'lesson_slug', flat=True
        )
    )
    level2_count = len(completed & LEVEL2_LESSONS)
    level3_count = len(completed & LEVEL3_LESSONS)

    learned_count = LearnedItem.objects.filter(student=user).count()
    flashcard_count = PersonalFlashcard.objects.filter(student=user).count()
    test_count = StudentTestSubmission.objects.filter(student=user).count()
    ai_reply_count = AIConversationUsage.objects.filter(
        student=user, kind='reply'
    ).count()

    achievements = [
        {
            'icon': '🏮',
            'name': 'Culture Explorer',
            'description': 'Complete your first Cultural Insight.',
            'earned': bool(completed),
            'progress': min(len(completed), 1),
            'goal': 1,
        },
        {
            'icon': '🐼🏮',
            'name': 'Level II Culture Enthusiast',
            'description': 'Complete all 6 Level II Cultural Insights.',
            'earned': level2_count == len(LEVEL2_LESSONS),
            'progress': level2_count,
            'goal': len(LEVEL2_LESSONS),
        },
        {
            'icon': '🐼🌏',
            'name': 'Level III Culture Enthusiast',
            'description': 'Complete all 6 Level III Cultural Insights.',
            'earned': level3_count == len(LEVEL3_LESSONS),
            'progress': level3_count,
            'goal': len(LEVEL3_LESSONS),
        },
        {
            'icon': '📚',
            'name': 'First Steps',
            'description': 'Learn your first PandaSpeak learning item.',
            'earned': learned_count >= 1,
            'progress': min(learned_count, 1),
            'goal': 1,
        },
        {
            'icon': '🌱',
            'name': 'Growing Learner',
            'description': 'Learn 25 vocabulary, sentence, or expression items.',
            'earned': learned_count >= 25,
            'progress': min(learned_count, 25),
            'goal': 25,
        },
        {
            'icon': '⭐',
            'name': 'Dedicated Learner',
            'description': 'Learn 100 vocabulary, sentence, or expression items.',
            'earned': learned_count >= 100,
            'progress': min(learned_count, 100),
            'goal': 100,
        },
        {
            'icon': '🈶',
            'name': 'Card Creator',
            'description': 'Create your first personal flash card.',
            'earned': flashcard_count >= 1,
            'progress': min(flashcard_count, 1),
            'goal': 1,
        },
        {
            'icon': '🤖',
            'name': 'Conversation Starter',
            'description': 'Practice your first AI Chinese conversation.',
            'earned': ai_reply_count >= 1,
            'progress': min(ai_reply_count, 1),
            'goal': 1,
        },
        {
            'icon': '💬',
            'name': 'Conversation Explorer',
            'description': 'Exchange 25 replies while practicing with AI.',
            'earned': ai_reply_count >= 25,
            'progress': min(ai_reply_count, 25),
            'goal': 25,
        },
        {
            'icon': '📋',
            'name': 'Test Taker',
            'description': 'Complete your first PandaSpeak test.',
            'earned': test_count >= 1,
            'progress': min(test_count, 1),
            'goal': 1,
        },
        {
            'icon': '🏅',
            'name': 'Practice Pays Off',
            'description': 'Complete 5 PandaSpeak tests.',
            'earned': test_count >= 5,
            'progress': min(test_count, 5),
            'goal': 5,
        },
    ]

    return {
        'achievements': achievements,
        'earned_count': sum(1 for item in achievements if item['earned']),
        'total_count': len(achievements),
    }
