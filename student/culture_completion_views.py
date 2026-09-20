from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from .culture_views import CULTURE_LESSONS, CULTURE_PREVIEW_CARDS, _allowed_levels
from .models import CulturalInsight, CulturalInsightCompletion, CulturalInsightUnlock


@login_required
def cultural_insights(request):
    level = getattr(request.user, 'learning_level', 'level1') or 'level1'
    if level == 'level1':
        return render(request, 'student/cultural_insights.html', {
            'level_locked': True, 'insights': [], 'preview_cards': [],
        })

    allowed = _allowed_levels(request.user)
    insights = CulturalInsight.objects.filter(
        is_published=True, level__in=allowed
    ).order_by('level', 'order', 'title')
    unlocked = set(CulturalInsightUnlock.objects.filter(
        student=request.user
    ).values_list('insight_id', flat=True))
    cards = [{'insight': item, 'unlocked': item.id in unlocked} for item in insights]

    completed_slugs = set(CulturalInsightCompletion.objects.filter(
        student=request.user
    ).values_list('lesson_slug', flat=True))
    previews = []
    for card in CULTURE_PREVIEW_CARDS:
        if card['level'] in allowed:
            item = card.copy()
            item['completed'] = item['slug'] in completed_slugs
            previews.append(item)

    level2_total = sum(1 for card in CULTURE_PREVIEW_CARDS if card['level'] == 'level2')
    level3_total = sum(1 for card in CULTURE_PREVIEW_CARDS if card['level'] == 'level3')
    level2_completed = sum(1 for card in CULTURE_PREVIEW_CARDS if card['level'] == 'level2' and card['slug'] in completed_slugs)
    level3_completed = sum(1 for card in CULTURE_PREVIEW_CARDS if card['level'] == 'level3' and card['slug'] in completed_slugs)

    return render(request, 'student/cultural_insights.html', {
        'level_locked': False,
        'insights': cards,
        'preview_cards': previews,
        'student_level': level,
        'level2_completed': level2_completed,
        'level2_total': level2_total,
        'level3_completed': level3_completed,
        'level3_total': level3_total,
    })


@login_required
def cultural_preview_detail(request, slug):
    lesson = CULTURE_LESSONS.get(slug)
    if not lesson or lesson['level'] not in _allowed_levels(request.user):
        return redirect('cultural_insights')

    completion = CulturalInsightCompletion.objects.filter(
        student=request.user, lesson_slug=slug
    ).first()
    completed = completion is not None
    result = None
    selected = None

    if request.method == 'POST':
        selected = request.POST.get('answer')
        if selected:
            result = selected == lesson['quiz']['answer']
            if result:
                completion, _ = CulturalInsightCompletion.objects.get_or_create(
                    student=request.user, lesson_slug=slug
                )
                completed = True

    return render(request, 'student/cultural_preview_detail.html', {
        'lesson': lesson,
        'slug': slug,
        'quiz_result': result,
        'selected_answer': selected,
        'completed': completed,
        'completed_at': completion.completed_at if completion else None,
    })
