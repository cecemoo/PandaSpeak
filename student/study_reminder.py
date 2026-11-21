"""Study reminder notification.

When a student logs in, they get one Notification (plus a web push,
like the site's other reminders) recapping the words, sentences and
expressions they studied since their previous login, together with
their overall learning progress so far (the same counts the student
dashboard shows).

The recap window starts at whichever is later: the student's previous
login, or the moment the last study reminder was created. That way
every learned item is reported exactly once, however often the
student logs in. Nothing is created when nothing new was studied.
"""

from django.db.models import Q
from django.urls import reverse
from django.utils import timezone

from account.models import Notification
from account.push import send_push_to_user
from teacher.models import Idiom, Sentence, Vocabulary

from .models import LearnedItem

REMINDER_TITLE = '📚 Study Reminder: Welcome Back!'
MAX_ITEMS_PER_GROUP = 5


def _allowed_levels(user):
    student_level = getattr(user, 'learning_level', None)
    if student_level == 'level1':
        return ['level1', 'all']
    if student_level == 'level2':
        return ['level1', 'level2', 'all']
    return ['level1', 'level2', 'level3', 'all']


def _visible_materials(model, user, allowed_levels):
    return model.objects.filter(
        level__in=allowed_levels
    ).filter(
        Q(visibility='all') |
        Q(visibility='groups', allowed_groups__students=user)
    ).distinct().count()


def _progress_counts(user):
    """Same learned/total counts the student dashboard displays."""
    allowed_levels = _allowed_levels(user)
    total_vocabulary = _visible_materials(Vocabulary, user, allowed_levels)
    total_sentences = _visible_materials(Sentence, user, allowed_levels)
    total_expressions = _visible_materials(Idiom, user, allowed_levels)
    learned_vocabulary = LearnedItem.objects.filter(
        student=user, vocabulary__isnull=False,
        vocabulary__level__in=allowed_levels).count()
    learned_sentences = LearnedItem.objects.filter(
        student=user, sentence__isnull=False,
        sentence__level__in=allowed_levels).count()
    learned_expressions = LearnedItem.objects.filter(
        student=user, idiom__isnull=False,
        idiom__level__in=allowed_levels).count()
    total_materials = total_vocabulary + total_sentences + total_expressions
    total_learned = learned_vocabulary + learned_sentences + learned_expressions
    overall_progress = (
        round((total_learned / total_materials) * 100)
        if total_materials > 0 else 0
    )
    return {
        'learned_vocabulary': learned_vocabulary,
        'learned_sentences': learned_sentences,
        'learned_expressions': learned_expressions,
        'total_materials': total_materials,
        'total_learned': total_learned,
        'overall_progress': overall_progress,
    }


def _short(text, limit):
    text = (text or '').strip()
    if len(text) > limit:
        return text[:limit - 1].rstrip() + '…'
    return text


def _vocab_label(item):
    vocab = item.vocabulary
    label = vocab.word
    if vocab.pinyin:
        label += f' ({vocab.pinyin})'
    if vocab.meaning:
        label += f' — {_short(vocab.meaning, 60)}'
    return label


def _sentence_label(item):
    sentence = item.sentence
    label = _short(sentence.text, 50)
    if sentence.translation:
        label += f' — {_short(sentence.translation, 60)}'
    return label


def _idiom_label(item):
    idiom = item.idiom
    label = idiom.idiom
    if idiom.pinyin:
        label += f' ({idiom.pinyin})'
    if idiom.meaning:
        label += f' — {_short(idiom.meaning, 60)}'
    return label


def _group_lines(heading, items, label_fn):
    if not items:
        return []
    shown = items[:MAX_ITEMS_PER_GROUP]
    lines = [f'{heading} ({len(items)}):']
    lines.extend(f'• {label_fn(item)}' for item in shown)
    extra = len(items) - len(shown)
    if extra > 0:
        lines.append(f'…and {extra} more')
    return lines


def maybe_create_study_reminder(user, previous_login):
    """Create the login study reminder for ``user`` if there is
    anything new to recap. ``previous_login`` is the user's last_login
    value captured *before* this login updated it. Returns the
    Notification, or None when no reminder was due. Never raises for
    missing data; the caller still guards the login flow."""
    last_reminder = (
        Notification.objects.filter(user=user, title=REMINDER_TITLE)
        .order_by('-created_at').first()
    )
    window_start = previous_login
    if last_reminder is not None:
        if window_start is None or last_reminder.created_at > window_start:
            window_start = last_reminder.created_at
    if window_start is None:
        return None

    now = timezone.now()
    items = list(
        LearnedItem.objects.filter(
            student=user,
            learned_at__gt=window_start,
            learned_at__lte=now,
        ).select_related('vocabulary', 'sentence', 'idiom')
        .order_by('learned_at')
    )
    if not items:
        return None

    words = [i for i in items if i.vocabulary_id]
    sentences = [i for i in items if i.sentence_id]
    expressions = [i for i in items if i.idiom_id]

    lines = ['Here is what you studied during your last visit:', '']
    lines += _group_lines('Words', words, _vocab_label)
    lines += _group_lines('Sentences', sentences, _sentence_label)
    lines += _group_lines('Expressions', expressions, _idiom_label)

    progress = _progress_counts(user)
    lines += [
        '',
        'Your overall progress so far: '
        f"{progress['total_learned']} of {progress['total_materials']} "
        f"materials learned ({progress['overall_progress']}%) — "
        f"{progress['learned_vocabulary']} words · "
        f"{progress['learned_sentences']} sentences · "
        f"{progress['learned_expressions']} expressions.",
        'Keep it up — a little practice every day adds up!',
    ]
    message = '\n'.join(lines)
    link = reverse('student_dashboard')
    notification = Notification.objects.create(
        user=user, title=REMINDER_TITLE, message=message, link=link)
    try:
        send_push_to_user(user, REMINDER_TITLE, message, link)
    except Exception:
        pass
    return notification
