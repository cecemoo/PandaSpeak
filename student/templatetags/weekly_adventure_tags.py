from datetime import timedelta

from django import template
from django.utils import timezone

from student.culture_views import CULTURE_PREVIEW_CARDS
from student.models import AIConversationUsage, CulturalInsightCompletion, LearnedItem, PersonalFlashcard, StudentTestSubmission
from teacher.bingo_models import BingoCard

register = template.Library()

LEVEL2_CULTURE = {card['slug'] for card in CULTURE_PREVIEW_CARDS if card.get('level') == 'level2'}
LEVEL3_CULTURE = {card['slug'] for card in CULTURE_PREVIEW_CARDS if card.get('level') == 'level3'}


@register.inclusion_tag('student/_weekly_adventure.html', takes_context=True)
def weekly_adventure(context):
    """Build weekly missions plus the student's permanent Panda Chest collection."""
    request = context.get('request')
    user = getattr(request, 'user', None)
    if not user or not user.is_authenticated:
        return {}

    now = timezone.localtime()
    week_start = (now - timedelta(days=now.weekday())).replace(hour=0, minute=0, second=0, microsecond=0)
    week_end = week_start + timedelta(days=7)

    learned_week = LearnedItem.objects.filter(student=user, learned_at__gte=week_start, learned_at__lt=week_end).count()
    flashcard_week = PersonalFlashcard.objects.filter(student=user, created_at__gte=week_start, created_at__lt=week_end).count()
    ai_week = AIConversationUsage.objects.filter(student=user, kind='reply', created_at__gte=week_start, created_at__lt=week_end).exists()
    bingo_done = BingoCard.objects.filter(student=user, has_bingo=True, completed_at__gte=week_start, completed_at__lt=week_end).exists()
    test_week = StudentTestSubmission.objects.filter(student=user, submitted_at__gte=week_start, submitted_at__lt=week_end).exists()
    culture_week = CulturalInsightCompletion.objects.filter(student=user, completed_at__gte=week_start, completed_at__lt=week_end).exists()

    all_culture = set(CulturalInsightCompletion.objects.filter(student=user).values_list('lesson_slug', flat=True))
    level2_count = len(all_culture & LEVEL2_CULTURE)
    level3_count = len(all_culture & LEVEL3_CULTURE)
    level2_total = len(LEVEL2_CULTURE)
    level3_total = len(LEVEL3_CULTURE)

    learned_total = LearnedItem.objects.filter(student=user).count()
    flashcard_total = PersonalFlashcard.objects.filter(student=user).count()
    ai_total = AIConversationUsage.objects.filter(student=user, kind='reply').count()
    test_total = StudentTestSubmission.objects.filter(student=user).count()

    missions = [
        {'icon':'📚','label':'Learn 10 new items','done':learned_week >= 10,'detail':f'{min(learned_week,10)} / 10'},
        {'icon':'🈶','label':'Create a personal flash card','done':flashcard_week >= 1,'detail':'Done' if flashcard_week else '0 / 1'},
        {'icon':'🤖','label':'Practice an AI conversation','done':ai_week,'detail':'Done' if ai_week else '0 / 1'},
        {'icon':'🎯','label':'Complete a Bingo','done':bingo_done,'detail':'Done' if bingo_done else '0 / 1'},
        {'icon':'📋','label':'Complete a test','done':test_week,'detail':'Done' if test_week else '0 / 1'},
    ]
    learning_level = getattr(user, 'learning_level', 'level1') or 'level1'
    if learning_level in ('level2','level3'):
        missions.append({'icon':'🏮','label':'Explore Chinese culture','done':culture_week,'detail':'Done' if culture_week else 'Complete 1 Cultural Insight'})

    completed = sum(1 for mission in missions if mission['done'])
    mission_total = len(missions)
    progress = round((completed / mission_total) * 100) if mission_total else 0
    if completed >= mission_total and mission_total:
        chest = {'name':'Legendary Panda Chest','icon':'👑🎁','class':'legendary','message':'Amazing! You completed every mission this week.'}
    elif completed >= 3:
        chest = {'name':'Rare Panda Chest','icon':'✨🎁','class':'rare','message':'Great progress — your Rare Chest is unlocked!'}
    elif completed >= 1:
        chest = {'name':'Common Panda Chest','icon':'🎁','class':'common','message':'Nice start — keep going to upgrade your chest.'}
    else:
        chest = {'name':'Panda Chest','icon':'🔒🎁','class':'locked','message':'Complete a mission to unlock your first chest.'}

    # Permanent collection decorations. Each category has a starter and mastery reward.
    rewards = [
        {'key':'culture','icon':'🏮','master_icon':'🌸','name':'Culture','earned':bool(all_culture),'mastered':bool(level2_total and level3_total and level2_count == level2_total and level3_count == level3_total),'detail':f'{level2_count + level3_count} insights explored'},
        {'key':'learning','icon':'📚','master_icon':'⭐','name':'Learning','earned':learned_total >= 1,'mastered':learned_total >= 100,'detail':f'{learned_total} items learned'},
        {'key':'conversation','icon':'💬','master_icon':'🤖','name':'Conversation','earned':ai_total >= 1,'mastered':ai_total >= 25,'detail':f'{ai_total} AI replies'},
        {'key':'tests','icon':'📋','master_icon':'🏅','name':'Tests','earned':test_total >= 1,'mastered':test_total >= 5,'detail':f'{test_total} tests completed'},
        {'key':'flashcards','icon':'🈶','master_icon':'✨','name':'Flash Cards','earned':flashcard_total >= 1,'mastered':flashcard_total >= 10,'detail':f'{flashcard_total} cards created'},
    ]
    earned_rewards = sum(1 for reward in rewards if reward['earned'])
    mastered_rewards = sum(1 for reward in rewards if reward['mastered'])
    if mastered_rewards == len(rewards):
        collection_title, collection_class = 'Legendary Learning Panda Chest', 'collection-legendary'
        collection_message = 'Every permanent Panda Chest decoration has reached mastery!'
    elif earned_rewards == len(rewards):
        collection_title, collection_class = 'Golden Learning Panda Chest', 'collection-gold'
        collection_message = 'You collected a reward from every PandaSpeak learning category!'
    elif earned_rewards >= 3:
        collection_title, collection_class = 'Growing Learning Panda Chest', 'collection-growing'
        collection_message = 'Your chest is filling with rewards from across PandaSpeak.'
    elif earned_rewards:
        collection_title, collection_class = 'Learning Panda Chest', 'collection-started'
        collection_message = 'Your permanent collection has begun!'
    else:
        collection_title, collection_class = 'Learning Panda Chest', 'collection-locked'
        collection_message = 'Complete an achievement to add your first permanent decoration.'

    collection = {
        'title': collection_title,
        'class': collection_class,
        'message': collection_message,
        'earned': earned_rewards,
        'mastered': mastered_rewards,
        'total': len(rewards),
        'rewards': rewards,
    }

    days_left = max(0, (week_end.date() - now.date()).days)
    return {'missions':missions,'completed':completed,'mission_total':mission_total,'progress':progress,'chest':chest,'collection':collection,'days_left':days_left}
