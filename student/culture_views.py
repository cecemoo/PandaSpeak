from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .models import CulturalInsight, CulturalInsightUnlock


CULTURE_PREVIEW_CARDS = [
    {'level': 'level2', 'category': 'festival', 'chinese_title': '紅包文化', 'title': 'Red Envelopes', 'summary': 'Learn when red envelopes are given and what they represent.', 'art': '🧧', 'theme': 'red'},
    {'level': 'level2', 'category': 'food', 'chinese_title': '餐桌禮儀', 'title': 'Dining Etiquette', 'summary': 'Explore common table manners and dining customs.', 'art': '🥢', 'theme': 'food'},
    {'level': 'level2', 'category': 'daily', 'chinese_title': '茶文化', 'title': 'Tea Culture', 'summary': 'Discover the role of tea in hospitality and everyday life.', 'art': '🍵', 'theme': 'tea'},
    {'level': 'level2', 'category': 'daily', 'chinese_title': '送禮文化', 'title': 'Gift Giving', 'summary': 'Learn thoughtful gift-giving customs and cultural considerations.', 'art': '🎁', 'theme': 'gift'},
    {'level': 'level2', 'category': 'society', 'chinese_title': '吉利與不吉利的數字', 'title': 'Lucky and Unlucky Numbers', 'summary': 'See why certain numbers carry special cultural meanings.', 'art': '福', 'theme': 'lucky'},
    {'level': 'level2', 'category': 'society', 'chinese_title': '家庭稱謂與關係', 'title': 'Family and Forms of Address', 'summary': 'Understand family relationships and respectful ways to address people.', 'art': '👨‍👩‍👧‍👦', 'theme': 'family'},
    {'level': 'level3', 'category': 'history', 'chinese_title': '歷史的影響', 'title': 'Historical Influences', 'summary': 'Explore how history continues to shape language and culture.', 'art': '🏯', 'theme': 'history'},
    {'level': 'level3', 'category': 'regional', 'chinese_title': '兩岸三地文化差異', 'title': 'Taiwan, Mainland and Hong Kong', 'summary': 'Compare regional language, customs, and everyday cultural differences.', 'art': '🌏', 'theme': 'regional'},
    {'level': 'level3', 'category': 'festival', 'chinese_title': '傳統節日的現代意義', 'title': 'Traditional Festivals Today', 'summary': 'See how traditional celebrations continue in modern life.', 'art': '🏮', 'theme': 'festival'},
    {'level': 'level3', 'category': 'modern', 'chinese_title': '職場文化', 'title': 'Workplace Etiquette', 'summary': 'Learn cultural expectations for professional communication and relationships.', 'art': '🤝', 'theme': 'work'},
    {'level': 'level3', 'category': 'language', 'chinese_title': '含蓄的溝通方式', 'title': 'Indirect Communication', 'summary': 'Understand context, politeness, and meaning beyond literal words.', 'art': '💬', 'theme': 'language'},
    {'level': 'level3', 'category': 'modern', 'chinese_title': '當代華語社會', 'title': 'Modern Chinese Society', 'summary': 'Explore contemporary life, technology, media, and changing traditions.', 'art': '🌃', 'theme': 'modern'},
]


@login_required
def cultural_insights(request):
    level = getattr(request.user, 'learning_level', 'level1') or 'level1'
    if level == 'level1':
        return render(request, 'student/cultural_insights.html', {'level_locked': True, 'insights': [], 'preview_cards': []})

    allowed_levels = ['level2'] if level == 'level2' else ['level2', 'level3']
    insights = CulturalInsight.objects.filter(is_published=True, level__in=allowed_levels).order_by('level', 'order', 'title')
    unlocked_ids = set(CulturalInsightUnlock.objects.filter(student=request.user).values_list('insight_id', flat=True))
    cards = [{'insight': insight, 'unlocked': insight.id in unlocked_ids} for insight in insights]
    preview_cards = [card for card in CULTURE_PREVIEW_CARDS if card['level'] in allowed_levels]
    return render(request, 'student/cultural_insights.html', {'level_locked': False, 'insights': cards, 'preview_cards': preview_cards, 'student_level': level})


@login_required
def cultural_insight_detail(request, pk):
    level = getattr(request.user, 'learning_level', 'level1') or 'level1'
    allowed_levels = ['level2'] if level == 'level2' else (['level2', 'level3'] if level == 'level3' else [])
    insight = get_object_or_404(CulturalInsight, pk=pk, is_published=True, level__in=allowed_levels)
    unlocked = CulturalInsightUnlock.objects.filter(student=request.user, insight=insight).exists()
    return render(request, 'student/cultural_insight_detail.html', {'insight': insight, 'unlocked': unlocked})


@login_required
@require_POST
def unlock_cultural_insight(request, pk):
    level = getattr(request.user, 'learning_level', 'level1') or 'level1'
    allowed_levels = ['level2'] if level == 'level2' else (['level2', 'level3'] if level == 'level3' else [])
    insight = get_object_or_404(CulturalInsight, pk=pk, is_published=True, level__in=allowed_levels)
    CulturalInsightUnlock.objects.get_or_create(student=request.user, insight=insight)
    return redirect('cultural_insight_detail', pk=insight.pk)
