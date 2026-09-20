from datetime import timedelta

from django import template
from django.utils import timezone

from student.models import AIConversationUsage, LearnedItem, PersonalFlashcard, StudentTestSubmission
from teacher.bingo_models import BingoCard

register = template.Library()


@register.inclusion_tag('student/_weekly_adventure.html', takes_context=True)
def weekly_adventure(context):
    """Build the student's weekly adventure from activity PandaSpeak already records."""
    request = context.get('request')
    user = getattr(request, 'user', None)
    if not user or not user.is_authenticated:
        return {}

    now = timezone.localtime()
    week_start = (now - timedelta(days=now.weekday())).replace(
        hour=0, minute=0, second=0, microsecond=0
    )
    week_end = week_start + timedelta(days=7)

    learned_count = LearnedItem.objects.filter(
        student=user, learned_at__gte=week_start, learned_at__lt=week_end
    ).count()
    flashcard_count = PersonalFlashcard.objects.filter(
        student=user, created_at__gte=week_start, created_at__lt=week_end
    ).count()
    ai_done = AIConversationUsage.objects.filter(
        student=user,
        kind='reply',
        created_at__gte=week_start,
        created_at__lt=week_end,
    ).exists()
    bingo_done = BingoCard.objects.filter(
        student=user,
        has_bingo=True,
        completed_at__gte=week_start,
        completed_at__lt=week_end,
    ).exists()
    test_done = StudentTestSubmission.objects.filter(
        student=user,
        submitted_at__gte=week_start,
        submitted_at__lt=week_end,
    ).exists()

    missions = [
        {'icon': '📚', 'label': 'Learn 10 new items', 'done': learned_count >= 10, 'detail': f'{min(learned_count, 10)} / 10'},
        {'icon': '🈶', 'label': 'Create a personal flash card', 'done': flashcard_count >= 1, 'detail': 'Done' if flashcard_count else '0 / 1'},
        {'icon': '🤖', 'label': 'Practice an AI conversation', 'done': ai_done, 'detail': 'Done' if ai_done else '0 / 1'},
        {'icon': '🎯', 'label': 'Complete a Bingo', 'done': bingo_done, 'detail': 'Done' if bingo_done else '0 / 1'},
        {'icon': '📋', 'label': 'Complete a test', 'done': test_done, 'detail': 'Done' if test_done else '0 / 1'},
    ]
    completed = sum(1 for mission in missions if mission['done'])
    progress = completed * 20

    if completed >= 5:
        chest = {'name': 'Legendary Panda Chest', 'icon': '👑🎁', 'class': 'legendary', 'message': 'Amazing! You completed every mission this week.'}
    elif completed >= 3:
        chest = {'name': 'Rare Panda Chest', 'icon': '✨🎁', 'class': 'rare', 'message': 'Great progress — your Rare Chest is unlocked!'}
    elif completed >= 1:
        chest = {'name': 'Common Panda Chest', 'icon': '🎁', 'class': 'common', 'message': 'Nice start — keep going to upgrade your chest.'}
    else:
        chest = {'name': 'Panda Chest', 'icon': '🔒🎁', 'class': 'locked', 'message': 'Complete a mission to unlock your first chest.'}

    days_left = max(0, (week_end.date() - now.date()).days)
    return {
        'missions': missions,
        'completed': completed,
        'progress': progress,
        'chest': chest,
        'days_left': days_left,
    }
