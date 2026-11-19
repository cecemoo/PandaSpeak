import random

from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import render

from teacher.models import Idiom, Vocabulary

LEVELS = {'level1': 'Level I', 'level2': 'Level II', 'level3': 'Level III'}
MAX_ITEMS = 80


def _selected_level(request):
    requested = request.GET.get('level')
    if requested in LEVELS:
        return requested
    current = getattr(request.user, 'learning_level', 'level1') or 'level1'
    return current if current in LEVELS else 'level1'


def _visible(qs, user, level):
    return qs.filter(level=level).filter(
        Q(visibility='all') | Q(visibility='groups', allowed_groups__students=user)
    ).distinct()


@login_required
def word_drop(request):
    current_level = getattr(request.user, 'learning_level', 'level1') or 'level1'
    if current_level not in LEVELS:
        current_level = 'level1'
    return render(request, 'student/word_drop.html', {
        'drop_level': current_level,
        'drop_level_label': LEVELS[current_level],
        'drop_levels': LEVELS,
    })


@login_required
def word_drop_items(request):
    level = _selected_level(request)
    items = []

    vocab = _visible(Vocabulary.objects.exclude(word=''), request.user, level)
    for v in vocab:
        meaning = (v.english_translation or v.meaning or '').strip()
        if meaning:
            items.append({'text': v.word, 'pinyin': v.pinyin or '', 'meaning': meaning, 'kind': 'word'})

    idioms = _visible(Idiom.objects.exclude(idiom=''), request.user, level)
    for i in idioms:
        meaning = (i.english_translation or '').strip()
        if meaning:
            items.append({'text': i.idiom, 'pinyin': i.pinyin or '', 'meaning': meaning, 'kind': 'idiom'})

    if len(items) < 8:
        return JsonResponse(
            {'error': f'Not enough words and expressions are available for {LEVELS[level]} yet.'},
            status=404,
        )
    random.shuffle(items)
    return JsonResponse({'level': level, 'items': items[:MAX_ITEMS]})
