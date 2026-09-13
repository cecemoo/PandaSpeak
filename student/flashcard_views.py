import random

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from subscription.decorators import subscription_required
from teacher.models import Idiom, Sentence, Vocabulary
from .models import PersonalFlashcard


DECKS = {
    'vocabulary': 'Vocabulary',
    'sentence': 'Sentences',
    'expression': 'Expressions',
    'personal': 'My Flash Cards',
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


def _personal_cards(student):
    items = PersonalFlashcard.objects.filter(student=student)
    return [
        {
            'front': item.front,
            'pinyin': item.pinyin or '',
            'meaning': item.meaning or '',
            'secondary': item.notes or '',
            'example': item.example or '',
            'example_pinyin': '',
            'example_translation': '',
            'audio': '',
        }
        for item in items
    ]


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
    elif deck == 'personal':
        cards = _personal_cards(request.user)
    else:
        cards = _vocabulary_cards(request.user)

    cards = list(cards)
    random.shuffle(cards)

    return render(request, 'student/flashcards.html', {
        'deck': deck,
        'deck_name': DECKS[deck],
        'cards': cards,
    })


@login_required(login_url='my_login')
@subscription_required
def manage_personal_flashcards(request):
    if request.method == 'POST':
        front = (request.POST.get('front') or '').strip()
        pinyin = (request.POST.get('pinyin') or '').strip()
        meaning = (request.POST.get('meaning') or '').strip()
        example = (request.POST.get('example') or '').strip()
        notes = (request.POST.get('notes') or '').strip()

        if not front or not meaning:
            messages.error(request, 'Chinese/front text and meaning are required.')
        else:
            PersonalFlashcard.objects.create(
                student=request.user,
                front=front,
                pinyin=pinyin,
                meaning=meaning,
                example=example,
                notes=notes,
            )
            messages.success(request, 'Your flash card was created.')
            return redirect('student_personal_flashcards')

    cards = PersonalFlashcard.objects.filter(student=request.user)
    return render(request, 'student/personal_flashcards.html', {
        'personal_cards': cards,
    })


@login_required(login_url='my_login')
@subscription_required
@require_POST
def delete_personal_flashcard(request, pk):
    card = get_object_or_404(PersonalFlashcard, pk=pk, student=request.user)
    card.delete()
    messages.success(request, 'Flash card deleted.')
    return redirect('student_personal_flashcards')
