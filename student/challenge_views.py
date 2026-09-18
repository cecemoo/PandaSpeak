import random

from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import render

from subscription.decorators import subscription_required
from teacher.models import Vocabulary, Sentence, Idiom

LEVELS = {'level1': 'Level I', 'level2': 'Level II', 'level3': 'Level III'}


def _selected_level(request):
    requested = request.GET.get('level')
    if requested in LEVELS:
        return requested
    current = getattr(request.user, 'learning_level', 'level1') or 'level1'
    return current if current in LEVELS else 'level1'


def _visible(qs, user, level):
    """Challenge games intentionally use only the selected level's material."""
    return qs.filter(level=level).filter(
        Q(visibility='all') | Q(visibility='groups', allowed_groups__students=user)
    ).distinct()


@login_required
@subscription_required
def chinese_challenge(request):
    current_level = getattr(request.user, 'learning_level', 'level1') or 'level1'
    if current_level not in LEVELS:
        current_level = 'level1'
    return render(request, 'student/chinese_challenge.html', {
        'challenge_level': current_level,
        'challenge_level_label': LEVELS[current_level],
        'challenge_levels': LEVELS,
    })


@login_required
@subscription_required
def challenge_question(request):
    mode = request.GET.get('mode', 'meaning')
    level = _selected_level(request)

    if mode in ('listen', 'word'):
        qs = _visible(
            Vocabulary.objects.filter(audio_file__isnull=False).exclude(audio_file='').exclude(word=''),
            request.user, level
        )
        items = list(qs)
        usable = [v for v in items if (v.english_translation or v.meaning)]
        if len(usable) < 4:
            return JsonResponse({'error': f'At least four vocabulary items with audio are needed for {LEVELS[level]} Listen & Guess.'}, status=404)
        item = random.choice(usable)
        answer = item.english_translation or item.meaning
        wrong_pool = []
        for v in usable:
            meaning = v.english_translation or v.meaning
            if meaning and meaning != answer and meaning not in wrong_pool:
                wrong_pool.append(meaning)
        if len(wrong_pool) < 3:
            return JsonResponse({'error': f'Not enough different meanings are available for {LEVELS[level]} Listen & Guess.'}, status=404)
        choices = [answer] + random.sample(wrong_pool, 3)
        random.shuffle(choices)
        return JsonResponse({
            'mode': 'listen', 'level': level, 'level_label': LEVELS[level],
            'audio_url': item.audio_file.url, 'answer': answer, 'choices': choices,
            'word': item.word, 'pinyin': item.pinyin,
        })

    if mode == 'sentence':
        items = list(_visible(Sentence.objects.exclude(text=''), request.user, level).values('text','translation','pinyin'))
        if not items:
            return JsonResponse({'error': f'No sentences are available for {LEVELS[level]} yet.'}, status=404)
        item = random.choice(items)
        tiles = [c for c in item['text'].strip() if not c.isspace()]
        if len(tiles) < 2:
            return JsonResponse({'error':'Not enough sentence material for a puzzle yet.'}, status=404)
        shuffled = tiles[:]
        for _ in range(5):
            random.shuffle(shuffled)
            if shuffled != tiles: break
        return JsonResponse({'mode':'sentence','level':level,'level_label':LEVELS[level],'answer':''.join(tiles),'tiles':shuffled,'translation':item['translation'],'pinyin':item['pinyin']})

    pool = []
    for v in _visible(Vocabulary.objects.exclude(word=''), request.user, level):
        meaning = v.english_translation or v.meaning
        if meaning: pool.append((v.word, meaning, 'Vocabulary'))
    for i in _visible(Idiom.objects.exclude(idiom=''), request.user, level):
        meaning = i.english_translation or i.meaning
        if meaning: pool.append((i.idiom, meaning, 'Chinese Expression'))
    if len(pool) < 4:
        return JsonResponse({'error':f'At least four vocabulary/expression items are needed for {LEVELS[level]} Meaning Match.'}, status=404)
    answer = random.choice(pool)
    wrong_pool = []
    for x in pool:
        if x[1] != answer[1] and x[1] not in wrong_pool: wrong_pool.append(x[1])
    if len(wrong_pool) < 3:
        return JsonResponse({'error':f'Not enough different meanings are available for {LEVELS[level]} Meaning Match.'}, status=404)
    choices = [answer[1]] + random.sample(wrong_pool, 3)
    random.shuffle(choices)
    return JsonResponse({'mode':'meaning','level':level,'level_label':LEVELS[level],'prompt':answer[0],'kind':answer[2],'answer':answer[1],'choices':choices})
