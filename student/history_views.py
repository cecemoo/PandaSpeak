from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from .history_lessons import HISTORY_CARDS, HISTORY_LESSONS
from .models import HistoryLessonCompletion


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
    if not allowed:
        return render(request, 'student/chinese_history.html', {
            'level_locked': True,
            'lessons': [],
            'student_level': level,
            'completed_count': 0,
            'total_count': 0,
        })

    completed_slugs = set(HistoryLessonCompletion.objects.filter(
        student=request.user
    ).values_list('lesson_slug', flat=True))

    lessons = []
    for card in HISTORY_CARDS:
        if card['level'] in allowed:
            item = card.copy()
            item['completed'] = item['slug'] in completed_slugs
            lessons.append(item)

    return render(request, 'student/chinese_history.html', {
        'level_locked': False,
        'lessons': lessons,
        'student_level': level,
        'completed_count': sum(1 for item in lessons if item['completed']),
        'total_count': len(lessons),
    })


@login_required
def history_lesson_detail(request, slug):
    lesson = HISTORY_LESSONS.get(slug)
    if not lesson or lesson['level'] not in _allowed_history_levels(request.user):
        return redirect('chinese_history')

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
    })
