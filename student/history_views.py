from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from subscription.plan_access import is_plus

from .history_lessons import HISTORY_CARDS, HISTORY_LESSONS
from .models import HistoryLessonCompletion


HISTORY_PREVIEW_SLUG = 'oracle-bones'


def _allowed_history_levels(user):
    level = getattr(user, 'learning_level', 'level1') or 'level1'
    if level == 'level3':
        return ('level2', 'level3')
    if level == 'level2':
        return ('level2',)
    return ()


@login_required
def chinese_history(request):
    level = getattr(request.user, 'learning_level', 'level1') or 'level1'
    allowed = _allowed_history_levels(request.user)
    plus_active = is_plus(request.user)

    if not allowed:
        return render(request, 'student/chinese_history.html', {
            'level_locked': True,
            'lessons': [],
            'student_level': level,
            'completed_count': 0,
            'total_count': 0,
            'plus_active': plus_active,
            'preview_slug': HISTORY_PREVIEW_SLUG,
        })

    completed_slugs = set(HistoryLessonCompletion.objects.filter(
        student=request.user
    ).values_list('lesson_slug', flat=True))

    lessons = []
    for card in HISTORY_CARDS:
        if card['level'] in allowed:
            item = card.copy()
            item['completed'] = item['slug'] in completed_slugs
            item['is_preview'] = item['slug'] == HISTORY_PREVIEW_SLUG
            item['plus_locked'] = not plus_active and not item['is_preview']
            lessons.append(item)

    accessible_lessons = [item for item in lessons if not item['plus_locked']]

    return render(request, 'student/chinese_history.html', {
        'level_locked': False,
        'lessons': lessons,
        'student_level': level,
        'completed_count': sum(1 for item in accessible_lessons if item['completed']),
        'total_count': len(accessible_lessons),
        'plus_active': plus_active,
        'preview_slug': HISTORY_PREVIEW_SLUG,
    })


@login_required
def history_lesson_detail(request, slug):
    lesson = HISTORY_LESSONS.get(slug)
    if not lesson or lesson['level'] not in _allowed_history_levels(request.user):
        return redirect('chinese_history')

    # Standard Level II/III members may preview the first History lesson.
    # The rest of the journey is a PandaSpeak Plus benefit.
    if slug != HISTORY_PREVIEW_SLUG and not is_plus(request.user):
        return redirect('plus_upgrade')

    completion = HistoryLessonCompletion.objects.filter(
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
                completion, _ = HistoryLessonCompletion.objects.get_or_create(
                    student=request.user, lesson_slug=slug
                )
                completed = True

    return render(request, 'student/history_lesson_detail.html', {
        'lesson': lesson,
        'slug': slug,
        'quiz_result': result,
        'selected_answer': selected,
        'completed': completed,
        'completed_at': completion.completed_at if completion else None,
        'is_preview': slug == HISTORY_PREVIEW_SLUG and not is_plus(request.user),
        'plus_active': is_plus(request.user),
    })
