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


def _student_learning_items(student):
    levels = _allowed_levels(student)
    vocabulary = _visible_to_student(
        Vocabulary.objects.filter(level__in=levels).select_related('category'), student
    ).order_by('category__category_name', 'word')
    sentences = _visible_to_student(
        Sentence.objects.filter(level__in=levels).select_related('category'), student
    ).order_by('category__category_name', 'text')
    expressions = _visible_to_student(
        Idiom.objects.filter(level__in=levels).select_related('category'), student
    ).order_by('category__category_name', 'idiom')
    return vocabulary, sentences, expressions


def _categories_from_items(items):
    categories = {}
    for item in items:
        if item.category_id and item.category:
            categories[item.category_id] = item.category.category_name
    return [
        {'id': category_id, 'name': name}
        for category_id, name in sorted(categories.items(), key=lambda pair: pair[1].lower())
    ]


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


def _personal_card_audio(item):
    if item.source_vocabulary and item.source_vocabulary.audio_file:
        return item.source_vocabulary.audio_file.url
    if item.source_sentence and item.source_sentence.audio_file:
        return item.source_sentence.audio_file.url
    if item.source_idiom and item.source_idiom.audio_scenario_file:
        return item.source_idiom.audio_scenario_file.url

    # Backward compatibility for cards created before source links were added.
    vocabulary = Vocabulary.objects.filter(
        word=item.front,
        pinyin=item.pinyin,
    ).exclude(audio_file='').first()
    if vocabulary and vocabulary.audio_file:
        return vocabulary.audio_file.url

    sentence = Sentence.objects.filter(
        text=item.front,
        pinyin=item.pinyin,
    ).exclude(audio_file='').first()
    if sentence and sentence.audio_file:
        return sentence.audio_file.url

    idiom = Idiom.objects.filter(
        idiom=item.front,
        pinyin=item.pinyin,
    ).exclude(audio_scenario_file='').first()
    if idiom and idiom.audio_scenario_file:
        return idiom.audio_scenario_file.url

    return ''


def _personal_cards(student):
    items = PersonalFlashcard.objects.filter(student=student).select_related(
        'source_vocabulary',
        'source_sentence',
        'source_idiom',
    )
    return [
        {
            'front': item.front,
            'pinyin': item.pinyin or '',
            'meaning': item.meaning or '',
            'secondary': item.notes or '',
            'example': item.example or '',
            'example_pinyin': '',
            'example_translation': '',
            'audio': _personal_card_audio(item),
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
    vocabulary, sentences, expressions = _student_learning_items(request.user)
    vocabulary = list(vocabulary)
    sentences = list(sentences)
    expressions = list(expressions)

    if request.method == 'POST':
        action = request.POST.get('action', 'manual')

        if action == 'add_existing':
            item_type = (request.POST.get('item_type') or '').strip()
            item_id = request.POST.get('item_id')
            source = None
            source_fields = {
                'source_vocabulary': None,
                'source_sentence': None,
                'source_idiom': None,
            }

            if item_type == 'vocabulary':
                source = get_object_or_404(
                    _visible_to_student(
                        Vocabulary.objects.filter(level__in=_allowed_levels(request.user)),
                        request.user,
                    ),
                    pk=item_id,
                )
                front = source.word
                pinyin = source.pinyin or ''
                meaning = source.meaning or ''
                example = source.example_sentence or ''
                source_fields['source_vocabulary'] = source
            elif item_type == 'sentence':
                source = get_object_or_404(
                    _visible_to_student(
                        Sentence.objects.filter(level__in=_allowed_levels(request.user)),
                        request.user,
                    ),
                    pk=item_id,
                )
                front = source.text
                pinyin = source.pinyin or ''
                meaning = source.translation or ''
                example = ''
                source_fields['source_sentence'] = source
            elif item_type == 'expression':
                source = get_object_or_404(
                    _visible_to_student(
                        Idiom.objects.filter(level__in=_allowed_levels(request.user)),
                        request.user,
                    ),
                    pk=item_id,
                )
                front = source.idiom
                pinyin = source.pinyin or ''
                meaning = source.meaning or source.english_translation or ''
                example = source.example_sentence or ''
                source_fields['source_idiom'] = source
            else:
                messages.error(request, 'Please choose vocabulary, a sentence, or an expression.')
                return redirect('student_personal_flashcards')

            source_filter = {'student': request.user}
            if item_type == 'vocabulary':
                source_filter['source_vocabulary'] = source
            elif item_type == 'sentence':
                source_filter['source_sentence'] = source
            else:
                source_filter['source_idiom'] = source

            existing = PersonalFlashcard.objects.filter(**source_filter).first()
            if not existing:
                existing = PersonalFlashcard.objects.filter(
                    student=request.user,
                    front=front,
                    pinyin=pinyin,
                    meaning=meaning,
                    example=example,
                ).first()

            if existing:
                changed = False
                if item_type == 'vocabulary' and not existing.source_vocabulary_id:
                    existing.source_vocabulary = source
                    changed = True
                elif item_type == 'sentence' and not existing.source_sentence_id:
                    existing.source_sentence = source
                    changed = True
                elif item_type == 'expression' and not existing.source_idiom_id:
                    existing.source_idiom = source
                    changed = True
                if changed:
                    existing.save()
                messages.info(request, 'That item is already in My Flash Cards.')
            else:
                PersonalFlashcard.objects.create(
                    student=request.user,
                    front=front,
                    pinyin=pinyin,
                    meaning=meaning,
                    example=example,
                    **source_fields,
                )
                messages.success(request, f'“{front}” was added to My Flash Cards.')
            return redirect('student_personal_flashcards')

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
        'available_vocabulary': vocabulary,
        'available_sentences': sentences,
        'available_expressions': expressions,
        'vocabulary_categories': _categories_from_items(vocabulary),
        'sentence_categories': _categories_from_items(sentences),
        'expression_categories': _categories_from_items(expressions),
    })


@login_required(login_url='my_login')
@subscription_required
@require_POST
def delete_personal_flashcard(request, pk):
    card = get_object_or_404(PersonalFlashcard, pk=pk, student=request.user)
    card.delete()
    messages.success(request, 'Flash card deleted.')
    return redirect('student_personal_flashcards')
