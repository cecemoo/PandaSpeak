"""Comprehensive assessment tests requested from the student Test List page.

Cece's spec (2026-11-03, revised later the same day): every assessment —
listening, speaking, or speaking & listening — is generated instantly
from the student's chosen level's learning materials (vocabulary /
sentences / expressions) and assigned to that student only:

- Listening: listen-and-choose-the-English-meaning multiple choice,
  scored by the existing test flow.
- Speaking: read-aloud questions (the material's Chinese text); the
  student records their own voice. Once the test is submitted, it shows
  up on the manager dashboard and a manager scores the speaking part —
  managers are alerted when a submission is waiting (see
  student.timed_tests.notify_managers_speaking_submission).
- Mixed: a listening part followed by a speaking part.

A generated speaking or mixed test also records an AssessmentRequest,
already fulfilled and linked to the test: it is the paper trail the
manager grading pages use to recognise the test as manager-scored.

Fallback: when a level does not have enough material to generate a
speaking or mixed test, the request is instead recorded as a pending
AssessmentRequest and the support inbox is emailed, so the PandaSpeak
team can prepare the test by hand from the manager dashboard.
"""
import random

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect
from django.views.decorators.http import require_POST

from teacher.models import Idiom, Sentence, Vocabulary

from .models import (AssessmentRequest, DEFAULT_TEST_TIME_LIMIT_MINUTES,
                     LanguageTest, StudentTestSubmission, TestQuestion)

LEVEL_LABELS = {'level1': 'Level I', 'level2': 'Level II', 'level3': 'Level III'}
MAX_QUESTIONS = 20
MIN_QUESTIONS = 10
SPEAKING_QUESTION_COUNT = 10
MIXED_LISTENING_QUESTION_COUNT = 10
MIXED_SPEAKING_QUESTION_COUNT = 10
CHOICE_LETTERS = ('A', 'B', 'C', 'D')
LISTENING_PROMPT = 'Listen to the audio and choose the correct English meaning.'
SUPPORT_EMAIL = 'pandaspeaksupport@gmail.com'


def _material_answer(material, fields):
    for field in fields:
        text = (getattr(material, field) or '').strip()
        if text:
            return text
    return ''


def _type_pool(model, audio_field, answer_fields, levels):
    """Usable items of one content type: {answer_text: audio_name}.

    An item is usable when it is visible to everyone, sits at the requested
    level (or 'all'), has audio, and has a non-empty English answer text.
    Answer texts are deduplicated so distractors are always distinct.
    """
    materials = (
        model.objects.filter(visibility='all', level__in=levels)
        .exclude(**{f'{audio_field}__isnull': True})
        .exclude(**{audio_field: ''})
    )
    items = {}
    for material in materials:
        answer = _material_answer(material, answer_fields)
        audio_name = getattr(material, audio_field).name
        if answer and audio_name and answer not in items:
            items[answer] = audio_name
    return items


def _level_pools(level):
    levels = [level, 'all']
    return [
        _type_pool(Vocabulary, 'audio_file', ('english_translation', 'meaning'), levels),
        _type_pool(Sentence, 'audio_file', ('translation',), levels),
        _type_pool(Idiom, 'audio_scenario_file', ('english_translation', 'meaning'), levels),
    ]


def _build_listening_questions(level, limit, start_order=1):
    """Up to `limit` listen_mc questions sampled across the content types.

    Only a content type with at least 4 distinct answer texts can supply a
    correct answer plus 3 distinct distractors from its own pool, so
    smaller pools are skipped. The returned list may be shorter than
    `limit` when the level does not have enough usable material — callers
    check the length against their minimum.
    """
    pools = [pool for pool in _level_pools(level) if len(pool) >= 4]
    combined = [
        (pool, answer, audio_name)
        for pool in pools
        for answer, audio_name in pool.items()
    ]
    random.shuffle(combined)
    combined = combined[:limit]

    questions = []
    for offset, (pool, answer, audio_name) in enumerate(combined):
        distractors = random.sample(
            [text for text in pool if text != answer], 3)
        choices = distractors + [answer]
        random.shuffle(choices)
        question = TestQuestion(
            question_type='listen_mc',
            prompt=LISTENING_PROMPT,
            choice_a=choices[0],
            choice_b=choices[1],
            choice_c=choices[2],
            choice_d=choices[3],
            correct_answer=CHOICE_LETTERS[choices.index(answer)],
            points=1,
            order=start_order + offset,
        )
        question.audio = audio_name
        questions.append(question)
    return questions


def _speaking_texts(level):
    """Distinct Chinese texts at the level that a student can read aloud.

    Speaking needs no recorded audio — the student records their own
    voice — so any visible material with a non-empty Chinese text counts.
    """
    levels = [level, 'all']
    texts = []
    seen = set()
    for model, field in ((Vocabulary, 'word'), (Sentence, 'text'), (Idiom, 'idiom')):
        values = model.objects.filter(
            visibility='all', level__in=levels).values_list(field, flat=True)
        for value in values:
            text = (value or '').strip()
            if text and text not in seen:
                seen.add(text)
                texts.append(text)
    return texts


def _build_speaking_questions(level, count, start_order=1):
    """Up to `count` speak_read questions sampled across the content types.

    The returned list may be shorter than `count` when the level does not
    have enough distinct texts — callers check the length.
    """
    texts = _speaking_texts(level)
    random.shuffle(texts)
    return [
        TestQuestion(
            question_type='speak_read',
            prompt=text,
            points=1,
            order=start_order + offset,
        )
        for offset, text in enumerate(texts[:count])
    ]


def _existing_open_test(user, level_label, test_type):
    completed_ids = StudentTestSubmission.objects.filter(
        student=user).values_list('test_id', flat=True)
    return (
        LanguageTest.objects.filter(
            assigned_students=user, test_type=test_type, level=level_label,
            is_active=True, is_published=True)
        .exclude(id__in=completed_ids)
        .order_by('id')
        .first()
    )


def _create_generated_test(user, level_label, test_type, title, description, questions):
    with transaction.atomic():
        test = LanguageTest.objects.create(
            title=title,
            level=level_label,
            test_type=test_type,
            description=description,
            is_active=True,
            is_published=True,
            teacher=None,
            time_limit_minutes=DEFAULT_TEST_TIME_LIMIT_MINUTES,
        )
        test.assigned_students.add(user)
        for question in questions:
            question.test = test
        TestQuestion.objects.bulk_create(questions)
    return test


def generate_listening_assessment(user, level):
    """Return the student's open listening assessment for the level.

    Reuses the existing uncompleted one when there is one; otherwise builds
    a new test from the level's materials. Returns None when fewer than
    MIN_QUESTIONS questions can be built (nothing is created then).
    """
    level_label = LEVEL_LABELS[level]
    existing = _existing_open_test(user, level_label, 'listening')
    if existing is not None:
        return existing

    questions = _build_listening_questions(level, MAX_QUESTIONS)
    if len(questions) < MIN_QUESTIONS:
        return None

    return _create_generated_test(
        user, level_label, 'listening',
        title=f'{level_label} Listening Assessment',
        description="Auto-generated listening assessment built from your level's learning materials.",
        questions=questions,
    )


def generate_speaking_assessment(user, level, test_type):
    """Return the student's open speaking or mixed assessment for the level.

    `test_type` is 'speaking' or 'mixed'. Like the listening path, an
    uncompleted test of the same level and type is reused. A newly created
    test also records its AssessmentRequest as fulfilled, linked to the
    test. Returns None when the level lacks the material for the minimum
    question counts (nothing is created then, and the caller falls back
    to the pending-request flow).
    """
    level_label = LEVEL_LABELS[level]
    existing = _existing_open_test(user, level_label, test_type)
    if existing is not None:
        return existing

    if test_type == 'speaking':
        questions = _build_speaking_questions(level, SPEAKING_QUESTION_COUNT)
        if len(questions) < SPEAKING_QUESTION_COUNT:
            return None
        title = f'{level_label} Speaking Assessment'
        description = (
            "Auto-generated speaking assessment built from your level's "
            "learning materials. Read each item aloud and record yourself "
            "— the PandaSpeak team will score your recordings.")
    else:  # mixed: listening questions first, then speaking ones.
        listening_questions = _build_listening_questions(
            level, MIXED_LISTENING_QUESTION_COUNT)
        speaking_questions = _build_speaking_questions(
            level, MIXED_SPEAKING_QUESTION_COUNT,
            start_order=len(listening_questions) + 1)
        if (len(listening_questions) < MIXED_LISTENING_QUESTION_COUNT
                or len(speaking_questions) < MIXED_SPEAKING_QUESTION_COUNT):
            return None
        questions = listening_questions + speaking_questions
        title = f'{level_label} Speaking & Listening Assessment'
        description = (
            "Auto-generated speaking & listening assessment built from "
            "your level's learning materials. The listening questions are "
            "scored automatically; the PandaSpeak team will score your "
            "speaking recordings.")

    with transaction.atomic():
        test = _create_generated_test(
            user, level_label, test_type,
            title=title, description=description, questions=questions)
        AssessmentRequest.objects.create(
            student=user, level=level, test_type=test_type,
            status='fulfilled', fulfilled_test=test)
    return test


def _record_pending_request(request, level, test_type):
    """Fallback for speaking/mixed when instant generation is impossible:
    record a pending request and alert the support inbox so the PandaSpeak
    team can prepare the test by hand from the manager dashboard."""
    if AssessmentRequest.objects.filter(
            student=request.user, level=level, test_type=test_type,
            status='pending').exists():
        messages.info(request, 'You already have a pending request for this assessment.')
        return redirect('test_list')

    AssessmentRequest.objects.create(
        student=request.user, level=level, test_type=test_type)
    level_label = LEVEL_LABELS[level]
    type_label = dict(AssessmentRequest.TEST_TYPE_CHOICES)[test_type]
    student_name = request.user.get_full_name() or request.user.first_name or request.user.email
    try:
        send_mail(
            subject=f'Assessment Test Request: {level_label} {type_label}',
            message=(
                f'A student has requested a comprehensive assessment test.\n\n'
                f'Student: {student_name}\n'
                f'Email: {request.user.email}\n'
                f'Level: {level_label}\n'
                f'Test type: {type_label}\n\n'
                f'Please open the Manager Dashboard, go to Assessment '
                f'Tests, and use "Create test" next to this request — the '
                f'student is preselected as the audience. Add the questions '
                f'and publish the test; publishing marks this request '
                f'fulfilled automatically.'
            ),
            from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', None),
            recipient_list=[SUPPORT_EMAIL],
        )
    except Exception:
        # The request itself is recorded; a mail failure must not lose it.
        pass
    messages.success(
        request,
        'Your request has been sent to PandaSpeak. A manager will prepare '
        'your assessment test and it will appear here when it is ready.')
    return redirect('test_list')


@login_required(login_url='my_login')
@require_POST
def request_assessment(request):
    level = request.POST.get('level', '')
    test_type = request.POST.get('test_type', '')
    if level not in LEVEL_LABELS or test_type not in ('listening', 'speaking', 'mixed'):
        messages.error(request, 'Please choose a level and a test type.')
        return redirect('test_list')

    if test_type == 'listening':
        test = generate_listening_assessment(request.user, level)
        if test is None:
            messages.error(
                request,
                'There is not enough listening material at that level yet '
                'to build an assessment. Please try another level.')
            return redirect('test_list')
        messages.success(request, 'Your listening assessment is ready.')
        return redirect('take_test', test_id=test.id)

    # Speaking and mixed assessments are generated instantly too; the
    # student's speaking recordings are scored by a manager afterwards.
    test = generate_speaking_assessment(request.user, level, test_type)
    if test is not None:
        messages.success(
            request,
            'Your assessment is ready. After you submit it, the speaking '
            'part will be scored by the PandaSpeak team.')
        return redirect('take_test', test_id=test.id)
    return _record_pending_request(request, level, test_type)


@login_required(login_url='my_login')
@require_POST
def cancel_assessment_request(request, request_id):
    assessment_request = get_object_or_404(
        AssessmentRequest, id=request_id, student=request.user)
    if assessment_request.status == 'pending':
        assessment_request.status = 'cancelled'
        assessment_request.save(update_fields=['status', 'updated_at'])
        messages.success(request, 'Your assessment request has been cancelled.')
    return redirect('test_list')
