import random

from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import redirect, render

from subscription.decorators import subscription_required
from teacher.models import Idiom, Sentence, Vocabulary


DECKS = {
    'vocabulary': 'Vocabulary',
    'sentence': 'Sentences',
    'expression': 'Expressions',
}


def _allowed_levels(student):
    level = getattr(student, 'learning_level', 'level1')
    if level == 'level1':
        return ['level1', 'all']
    if level == 'level2':
        return ['level1', 'level2', 'all']
    if level == 'level3':
        return ['level1', 'level2', 'level3', 'all']
    return ['level1', 'level2', 'level3', 'all']


def _visible_to_student(queryset, student):
    return queryset.filter(
        Q(visibility='all') |
        Q(visibility='groups', allowed_groups__students=student)
    ).distinct()


def _vocabulary_cards(student):
    items = _visible_to_student(
        Vocabulary.objects.filter(level__in=_allowed_levels(student)),
        student,
    ).order_by('word')

    cards = []
    for item in items:
        cards.append({
            'front': item.word,
            'pinyin': item.pinyin or '',
            'meaning': item.meaning or '',
            'secondary': item.english_translation if hasattr(item, 'english_translation') else '',
            'example': item.example_sentence or '',
            'example_pinyin': item.example_pinyin or '',
            'example_translation': item.example_translation or '',
            'audio': item.audio_file.url if item.audio_file else '',
        })
    return cards


def _sentence_cards(student):
    items = _visible_to_student(
        Sentence.objects.filter(level__in=_allowed_levels(student)),
        student,
    ).order_by('text')

    cards = []
    for item in items:
        cards.append({
            'front': item.text,
            'pinyin': item.pinyin or '',
            'meaning': item.translation or '',
            'secondary': '',
            'example': '',
            'example_pinyin': '',
            'example_translation': '',
            'audio': item.audio_file.url if item.audio_file else '',
        })
    return cards


def _expression_cards(student):
    items = _visible_to_student(
        Idiom.objects.filter(level__in=_allowed_levels(student)),
        student,
    ).order_by('idiom')

    cards = []
    for item in items:
        audio = ''
        if getattr(item, 'audio_scenario_file', None):
            audio = item.audio_scenario_file.url
        cards.append({
            'front': item.idiom,
            'pinyin': item.pinyin or '',
            'meaning': item.meaning or '',
            'secondary': item.english_translation or '',
            'example': item.example_sentence or '',
            'example_pinyin': item.example_pinyin or '',
            'example_translation': item.example_translation or '',
            'audio': audio,
        })
    return cards


@login_required(login_url='my_login')
@subscription_required
def flashcards(request):
    deck = request.GET.get('deck', 'vocabulary')
    if deck not in DECKS:
        return redirect('student_flashcards')

    if deck == 'sentence':
        cards = _sentence_cards(request.user)
    elif deck == 'expression':
        cards = _expression_cards(request.user)
    else:
        cards = _vocabulary_cards(request.user)

    # Keep the first visit fresh without changing the student's stored materials.
    cards = list(cards)
    random.shuffle(cards)

    return render(request, 'student/flashcards.html', {
        'deck': deck,
        'deck_name': DECKS[deck],
        'cards': cards,
    })
