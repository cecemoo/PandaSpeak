import random

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render

from subscription.decorators import subscription_required
from teacher.models import Vocabulary, Sentence, Idiom


def _levels_for(user):
    level = getattr(user, 'learning_level', 'level1') or 'level1'
    if level == 'level3': return ['level1', 'level2', 'level3', 'all']
    if level == 'level2': return ['level1', 'level2', 'all']
    return ['level1', 'all']


def _visible(qs, user):
    return qs.filter(level__in=_levels_for(user)).filter(
        __import__('django').db.models.Q(visibility='all') |
        __import__('django').db.models.Q(visibility='groups', allowed_groups__students=user)
    ).distinct()


@login_required
@subscription_required
def chinese_challenge(request):
    return render(request, 'student/chinese_challenge.html')


@login_required
@subscription_required
def challenge_question(request):
    mode = request.GET.get('mode', 'meaning')

    if mode == 'word':
        items = list(_visible(Vocabulary.objects.exclude(word=''), request.user).values('word', 'pinyin', 'meaning', 'english_translation'))
        if not items: return JsonResponse({'error': 'No vocabulary is available for your level yet.'}, status=404)
        item = random.choice(items)
        clue = item['meaning'] or item['english_translation'] or item['pinyin']
        return JsonResponse({'mode':'word','answer':item['word'],'clue':clue,'pinyin':item['pinyin']})

    if mode == 'sentence':
        items = list(_visible(Sentence.objects.exclude(text=''), request.user).values('text','translation','pinyin'))
        if not items: return JsonResponse({'error': 'No sentences are available for your level yet.'}, status=404)
        item = random.choice(items)
        # Chinese sentences generally do not contain spaces, so use characters as
        # puzzle tiles; punctuation stays attached as a tile and can be reordered.
        tiles = [c for c in item['text'].strip() if not c.isspace()]
        if len(tiles) < 2: return JsonResponse({'error':'Not enough sentence material for a puzzle yet.'}, status=404)
        shuffled = tiles[:]
        for _ in range(5):
            random.shuffle(shuffled)
            if shuffled != tiles: break
        return JsonResponse({'mode':'sentence','answer':''.join(tiles),'tiles':shuffled,'translation':item['translation'],'pinyin':item['pinyin']})

    # Meaning Match randomly uses vocabulary or expressions and supplies four choices.
    pool = []
    for v in _visible(Vocabulary.objects.exclude(word=''), request.user):
        meaning = v.english_translation or v.meaning
        if meaning: pool.append((v.word, meaning, 'Vocabulary'))
    for i in _visible(Idiom.objects.exclude(idiom=''), request.user):
        meaning = i.english_translation or i.meaning
        if meaning: pool.append((i.idiom, meaning, 'Chinese Expression'))
    if len(pool) < 4: return JsonResponse({'error':'At least four vocabulary/expression items are needed for Meaning Match.'}, status=404)
    answer = random.choice(pool)
    wrong = random.sample([x for x in pool if x[1] != answer[1]], 3)
    choices = [answer[1]] + [x[1] for x in wrong]
    random.shuffle(choices)
    return JsonResponse({'mode':'meaning','prompt':answer[0],'kind':answer[2],'answer':answer[1],'choices':choices})
