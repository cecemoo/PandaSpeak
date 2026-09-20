from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .models import CulturalInsight, CulturalInsightUnlock


CULTURE_PREVIEW_CARDS = [
    {'slug': 'red-envelopes', 'level': 'level2', 'category': 'festival', 'chinese_title': '紅包文化', 'title': 'Red Envelopes', 'summary': 'Learn when red envelopes are given and what they represent.', 'art': '🧧', 'theme': 'red'},
    {'slug': '', 'level': 'level2', 'category': 'food', 'chinese_title': '餐桌禮儀', 'title': 'Dining Etiquette', 'summary': 'Explore common table manners and dining customs.', 'art': '🥢', 'theme': 'food'},
    {'slug': '', 'level': 'level2', 'category': 'daily', 'chinese_title': '茶文化', 'title': 'Tea Culture', 'summary': 'Discover the role of tea in hospitality and everyday life.', 'art': '🍵', 'theme': 'tea'},
    {'slug': '', 'level': 'level2', 'category': 'daily', 'chinese_title': '送禮文化', 'title': 'Gift Giving', 'summary': 'Learn thoughtful gift-giving customs and cultural considerations.', 'art': '🎁', 'theme': 'gift'},
    {'slug': '', 'level': 'level2', 'category': 'society', 'chinese_title': '吉利與不吉利的數字', 'title': 'Lucky and Unlucky Numbers', 'summary': 'See why certain numbers carry special cultural meanings.', 'art': '福', 'theme': 'lucky'},
    {'slug': '', 'level': 'level2', 'category': 'society', 'chinese_title': '家庭稱謂與關係', 'title': 'Family and Forms of Address', 'summary': 'Understand family relationships and respectful ways to address people.', 'art': '👨‍👩‍👧‍👦', 'theme': 'family'},
    {'slug': '', 'level': 'level3', 'category': 'history', 'chinese_title': '歷史的影響', 'title': 'Historical Influences', 'summary': 'Explore how history continues to shape language and culture.', 'art': '🏯', 'theme': 'history'},
    {'slug': '', 'level': 'level3', 'category': 'regional', 'chinese_title': '兩岸三地文化差異', 'title': 'Taiwan, Mainland and Hong Kong', 'summary': 'Compare regional language, customs, and everyday cultural differences.', 'art': '🌏', 'theme': 'regional'},
    {'slug': '', 'level': 'level3', 'category': 'festival', 'chinese_title': '傳統節日的現代意義', 'title': 'Traditional Festivals Today', 'summary': 'See how traditional celebrations continue in modern life.', 'art': '🏮', 'theme': 'festival'},
    {'slug': '', 'level': 'level3', 'category': 'modern', 'chinese_title': '職場文化', 'title': 'Workplace Etiquette', 'summary': 'Learn cultural expectations for professional communication and relationships.', 'art': '🤝', 'theme': 'work'},
    {'slug': '', 'level': 'level3', 'category': 'language', 'chinese_title': '含蓄的溝通方式', 'title': 'Indirect Communication', 'summary': 'Understand context, politeness, and meaning beyond literal words.', 'art': '💬', 'theme': 'language'},
    {'slug': '', 'level': 'level3', 'category': 'modern', 'chinese_title': '當代華語社會', 'title': 'Modern Chinese Society', 'summary': 'Explore contemporary life, technology, media, and changing traditions.', 'art': '🌃', 'theme': 'modern'},
]

CULTURE_LESSONS = {
    'red-envelopes': {
        'level': 'level2', 'category': 'Festivals & Traditions', 'art': '🧧',
        'chinese_title': '紅包文化', 'title': 'Red Envelope Culture',
        'intro': 'A red envelope is more than a gift of money. It is a way to share good wishes, luck, and blessings with someone you care about.',
        'sections': [
            {'icon': '🧧', 'title': 'What is a red envelope?', 'text': '紅包 (hóngbāo) is a red envelope containing money. Red represents good fortune and celebration in Chinese culture. The meaning is not simply the amount of money inside—the red envelope itself carries wishes for happiness, health, and prosperity.'},
            {'icon': '🗓️', 'title': 'When are red envelopes given?', 'text': 'They are especially common during Lunar New Year, when older family members give them to children or younger relatives. Red envelopes may also be given at weddings, birthdays, the birth of a baby, and other important celebrations. Customs can differ among Chinese-speaking communities and families.'},
            {'icon': '🤲', 'title': 'Giving and receiving politely', 'text': 'In more formal situations, giving or receiving a red envelope with both hands is a respectful gesture. A recipient normally thanks the giver. In many families, especially during Lunar New Year, children may offer an auspicious greeting before receiving their red envelope.'},
            {'icon': '🔢', 'title': 'The amount can carry meaning', 'text': 'People may choose amounts associated with good fortune. The number eight (八, bā) is often considered auspicious because its sound is associated with prosperity in some Chinese varieties. The number four (四, sì) is sometimes avoided because it sounds similar to the word for death (死, sǐ) in Mandarin and several other varieties.'},
        ],
        'vocabulary': [
            {'word': '紅包', 'pinyin': 'hóngbāo', 'meaning': 'red envelope'},
            {'word': '恭喜發財', 'pinyin': 'gōngxǐ fācái', 'meaning': 'Wishing you prosperity'},
            {'word': '新年快樂', 'pinyin': 'xīnnián kuàilè', 'meaning': 'Happy New Year'},
            {'word': '吉利', 'pinyin': 'jílì', 'meaning': 'auspicious; lucky'},
            {'word': '祝福', 'pinyin': 'zhùfú', 'meaning': 'blessing; good wishes'},
        ],
        'example': {'chinese': '祝你新年快樂，恭喜發財！', 'pinyin': 'Zhù nǐ xīnnián kuàilè, gōngxǐ fācái!', 'english': 'Wishing you a Happy New Year and prosperity!'},
        'did_you_know': 'Digital red envelopes are now common too. Messaging and payment apps have made it possible to send a virtual 紅包, combining a traditional custom with modern technology.',
        'quiz': {'question': 'What is the most important cultural idea behind giving a 紅包?', 'choices': [('a', 'Showing how wealthy the giver is'), ('b', 'Sharing good wishes, luck, and blessings'), ('c', 'Paying someone back'), ('d', 'Buying a holiday gift')], 'answer': 'b'},
    }
}


def _allowed_levels(user):
    level = getattr(user, 'learning_level', 'level1') or 'level1'
    return ['level2'] if level == 'level2' else (['level2', 'level3'] if level == 'level3' else [])


@login_required
def cultural_insights(request):
    level = getattr(request.user, 'learning_level', 'level1') or 'level1'
    if level == 'level1':
        return render(request, 'student/cultural_insights.html', {'level_locked': True, 'insights': [], 'preview_cards': []})
    allowed_levels = _allowed_levels(request.user)
    insights = CulturalInsight.objects.filter(is_published=True, level__in=allowed_levels).order_by('level', 'order', 'title')
    unlocked_ids = set(CulturalInsightUnlock.objects.filter(student=request.user).values_list('insight_id', flat=True))
    cards = [{'insight': insight, 'unlocked': insight.id in unlocked_ids} for insight in insights]
    preview_cards = [card for card in CULTURE_PREVIEW_CARDS if card['level'] in allowed_levels]
    return render(request, 'student/cultural_insights.html', {'level_locked': False, 'insights': cards, 'preview_cards': preview_cards, 'student_level': level})


@login_required
def cultural_preview_detail(request, slug):
    lesson = CULTURE_LESSONS.get(slug)
    if not lesson or lesson['level'] not in _allowed_levels(request.user):
        return redirect('cultural_insights')
    quiz_result = None
    selected_answer = None
    if request.method == 'POST':
        selected_answer = request.POST.get('answer')
        if selected_answer:
            quiz_result = selected_answer == lesson['quiz']['answer']
    return render(request, 'student/cultural_preview_detail.html', {'lesson': lesson, 'slug': slug, 'quiz_result': quiz_result, 'selected_answer': selected_answer})


@login_required
def cultural_insight_detail(request, pk):
    allowed_levels = _allowed_levels(request.user)
    insight = get_object_or_404(CulturalInsight, pk=pk, is_published=True, level__in=allowed_levels)
    unlocked = CulturalInsightUnlock.objects.filter(student=request.user, insight=insight).exists()
    return render(request, 'student/cultural_insight_detail.html', {'insight': insight, 'unlocked': unlocked})


@login_required
@require_POST
def unlock_cultural_insight(request, pk):
    allowed_levels = _allowed_levels(request.user)
    insight = get_object_or_404(CulturalInsight, pk=pk, is_published=True, level__in=allowed_levels)
    CulturalInsightUnlock.objects.get_or_create(student=request.user, insight=insight)
    return redirect('cultural_insight_detail', pk=insight.pk)
