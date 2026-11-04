"""Comprehensive assessment tests requested from the student Test List page.

Two paths (Cece's spec, 2026-11-03):

- Listening-only: generated instantly from the student's chosen level's
  learning materials (vocabulary / sentences / expressions with audio) as
  listen-and-choose-the-English-meaning multiple-choice questions, assigned
  to that student only, and scored by the existing test flow.
- Speaking or Speaking & Listening: recorded as an AssessmentRequest for
  the PandaSpeak team. A manager creates the test from the manager
  dashboard's Assessment Tests page (the requester is preselected as the
  audience); publishing the test marks the request fulfilled. The manager
  scores the speaking part while any listening part is auto-scored as usual.
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


def _existing_open_listening_test(user, level_label):
    completed_ids = StudentTestSubmission.objects.filter(
        student=user).values_list('test_id', flat=True)
    return (
        LanguageTest.objects.filter(
            assigned_students=user, test_type='listening', level=level_label,
            is_active=True, is_published=True)
        .exclude(id__in=completed_ids)
        .order_by('id')
        .first()
    )


def generate_listening_assessment(user, level):
    """Return the student's open listening assessment for the level.

    Reuses the existing uncompleted one when there is one; otherwise builds
    a new test from the level's materials. Returns None when fewer than
    MIN_QUESTIONS questions can be built (nothing is created then).
    """
    level_label = LEVEL_LABELS[level]
    existing = _existing_open_listening_test(user, level_label)
    if existing is not None:
        return existing

    # Only a content type with at least 4 distinct answer texts can supply a
    # correct answer plus 3 distinct distractors from its own pool.
    pools = [pool for pool in _level_pools(level) if len(pool) >= 4]
    combined = [
        (pool, answer, audio_name)
        for pool in pools
        for answer, audio_name in pool.items()
    ]
    random.shuffle(combined)
    combined = combined[:MAX_QUESTIONS]
    if len(combined) < MIN_QUESTIONS:
        return None

    questions = []
    for order, (pool, answer, audio_name) in enumerate(combined, start=1):
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
            order=order,
        )
        question.audio = audio_name
        questions.append(question)

    with transaction.atomic():
        test = LanguageTest.objects.create(
            title=f'{level_label} Listening Assessment',
            level=level_label,
            test_type='listening',
            description="Auto-generated listening assessment built from your level's learning materials.",
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
def cancel_assessment_request(request, request_id):
    assessment_request = get_object_or_404(
        AssessmentRequest, id=request_id, student=request.user)
    if assessment_request.status == 'pending':
        assessment_request.status = 'cancelled'
        assessment_request.save(update_fields=['status', 'updated_at'])
        messages.success(request, 'Your assessment request has been cancelled.')
    return redirect('test_list')
