from django import template

from student.models import CulturalInsightCompletion

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
    """Build Cultural Insight achievements without changing student views."""
    request = context.get('request')
    user = getattr(request, 'user', None)
    if not user or not user.is_authenticated:
        return {'achievements': [], 'earned_count': 0, 'total_count': 3}

    completed = set(
        CulturalInsightCompletion.objects.filter(student=user).values_list(
            'lesson_slug', flat=True
        )
    )
    level2_count = len(completed & LEVEL2_LESSONS)
    level3_count = len(completed & LEVEL3_LESSONS)

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
    ]

    return {
        'achievements': achievements,
        'earned_count': sum(1 for item in achievements if item['earned']),
        'total_count': len(achievements),
    }
