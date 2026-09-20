from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .models import CulturalInsight, CulturalInsightUnlock


@login_required
def cultural_insights(request):
    level = getattr(request.user, 'learning_level', 'level1') or 'level1'
    if level == 'level1':
        return render(request, 'student/cultural_insights.html', {'level_locked': True, 'insights': []})

    allowed_levels = ['level2'] if level == 'level2' else ['level2', 'level3']
    insights = CulturalInsight.objects.filter(is_published=True, level__in=allowed_levels).order_by('level', 'order', 'title')
    unlocked_ids = set(CulturalInsightUnlock.objects.filter(student=request.user).values_list('insight_id', flat=True))
    cards = [{'insight': insight, 'unlocked': insight.id in unlocked_ids} for insight in insights]
    return render(request, 'student/cultural_insights.html', {'level_locked': False, 'insights': cards, 'student_level': level})


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
