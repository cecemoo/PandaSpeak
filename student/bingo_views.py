import random

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone

from account.models import Notification
from account.push import send_push_to_user
from course.models import StudentGroup
from subscription.models import Subscription
from teacher.bingo_models import BingoCard, BingoGame
from teacher.models import Sentence, Vocabulary

LEVEL_ORDER = ['level1', 'level2', 'level3']
PUNCTUATION = set("，。！？；：,.!?;:、（）()「」『』“”\"' ")


def _student_can_play(game, student):
    if game.audience == 'subscribers':
        return not student.is_teacher and not student.is_staff and Subscription.objects.filter(user=student, is_active=True).exists()
    if game.audience == 'my_students':
        return student.groups_joined.filter(teacher=game.teacher, is_active=True).exists()
    return bool(game.student_group and game.student_group.students.filter(pk=student.pk, is_active=True).exists())


def _visibility_filter_for_game(game):
    if game.audience == 'subscribers':
        return Q(visibility='all')
    if game.audience == 'my_students':
        teacher_groups = StudentGroup.objects.filter(teacher=game.teacher, is_active=True)
        return Q(visibility='all') | Q(allowed_groups__in=teacher_groups)
    if game.student_group:
        return Q(visibility='all') | Q(allowed_groups=game.student_group)
    return Q(visibility='all')


def _eligible_materials(game, level=None):
    visibility_filter = _visibility_filter_for_game(game)
    selected_level = level or game.level
    level_filter = Q()
    if selected_level != 'all':
        level_filter = Q(level=selected_level) | Q(level='all')
    if game.game_mode == 'make_sentence':
        return Sentence.objects.filter(visibility_filter, level_filter).distinct()
    if game.content_type == 'sentence':
        return Sentence.objects.filter(visibility_filter, level_filter, audio_file__isnull=False).exclude(audio_file='').distinct()
    return Vocabulary.objects.filter(visibility_filter, level_filter, audio_file__isnull=False).exclude(audio_file='').distinct()


def _serialize_item(game, item):
    if isinstance(item, Sentence):
        return {'id': item.id, 'text': item.text, 'pinyin': item.pinyin, 'translation': item.translation, 'audio': item.audio_file.url if item.audio_file else '', 'free': False}
    return {'id': item.id, 'text': item.word, 'pinyin': item.pinyin, 'translation': item.english_translation, 'audio': item.audio_file.url if item.audio_file else '', 'free': False}


def _generate_cells(game, level):
    pool = list(_eligible_materials(game, level))
    if len(pool) < game.required_item_count:
        return None
    cells = [_serialize_item(game, item) for item in random.sample(pool, game.required_item_count)]
    if game.use_free_center and game.card_size % 2 == 1:
        center = (game.card_size * game.card_size) // 2
        cells.insert(center, {'id': None, 'text': 'FREE', 'pinyin': '自由格', 'translation': 'Free Space', 'audio': '', 'free': True})
    return cells


def _move_level(level, direction):
    if level not in LEVEL_ORDER:
        return level
    index = LEVEL_ORDER.index(level)
    return LEVEL_ORDER[max(0, min(len(LEVEL_ORDER) - 1, index + direction))]


def _assigned_level_for_student(game, student):
    if not game.adaptive_difficulty:
        return game.level
    previous_cards = list(BingoCard.objects.filter(student=student, game__game_mode=game.game_mode, has_bingo=True).order_by('-completed_at', '-created_at')[:3])
    base_level = previous_cards[0].assigned_level if previous_cards else (game.level if game.level in LEVEL_ORDER else 'level1')
    attempts = sum(card.correct_count + card.incorrect_count for card in previous_cards)
    correct = sum(card.correct_count for card in previous_cards)
    target_level = base_level
    if attempts >= 6:
        accuracy = correct / attempts
        if accuracy >= 0.80:
            target_level = _move_level(base_level, 1)
        elif accuracy < 0.50:
            target_level = _move_level(base_level, -1)
    for candidate in (target_level, base_level, game.level, 'all'):
        if _eligible_materials(game, candidate).count() >= game.required_item_count:
            return candidate
    return game.level


def _winning_positions(size):
    lines = [[row * size + col for col in range(size)] for row in range(size)]
    lines += [[row * size + col for row in range(size)] for col in range(size)]
    lines.append([i * size + i for i in range(size)])
    lines.append([i * size + (size - 1 - i) for i in range(size)])
    return lines


def _has_bingo(card):
    marked = set(card.marked_positions)
    return any(all(position in marked for position in line) for line in _winning_positions(card.game.card_size))


def _notify_teacher_of_bingo(card):
    teacher = card.game.teacher
    student_name = card.student.get_full_name() or card.student.email or card.student.username
    teacher_link = reverse('teacher_bingo_list')
    Notification.objects.create(user=teacher, title='Student Got Bingo!', message=f"{student_name} got Bingo in {card.game.title}, round {card.round_number}.", link=teacher_link)
    send_push_to_user(teacher, 'Student Got Bingo!', f'{student_name} completed round {card.round_number} of {card.game.title}.', teacher_link)
    if teacher.email:
        send_mail(subject=f'PandaSpeak Bingo: {student_name} got Bingo!', message=f"Hello {teacher.get_full_name() or teacher.email},\n\n{student_name} got Bingo in '{card.game.title}', round {card.round_number}.\nDifficulty: {card.assigned_level.replace('level', 'Level ')}\n\nBest regards,\nPandaSpeak Support Team", from_email=settings.DEFAULT_FROM_EMAIL, recipient_list=[teacher.email], fail_silently=True)


def _normalize_sentence(text):
    return ''.join(ch for ch in (text or '') if ch not in PUNCTUATION and not ch.isspace())


def _finish_attempt(card):
    previously_had_bingo = card.has_bingo
    card.has_bingo = _has_bingo(card)
    card.completed_at = timezone.now() if card.has_bingo else None
    if card.has_bingo and not previously_had_bingo and not card.teacher_notified:
        _notify_teacher_of_bingo(card)
        card.teacher_notified = True
    card.save()


def _create_round(game, student):
    assigned_level = _assigned_level_for_student(game, student)
    cells = _generate_cells(game, assigned_level)
    if cells is None:
        return None
    last_round = BingoCard.objects.filter(game=game, student=student).order_by('-round_number').first()
    round_number = (last_round.round_number + 1) if last_round else 1
    marked = [position for position, cell in enumerate(cells) if cell.get('free')]
    return BingoCard.objects.create(game=game, student=student, round_number=round_number, cells=cells, marked_positions=marked, assigned_level=assigned_level)


@login_required
def bingo_game_list(request):
    games = [game for game in BingoGame.objects.filter(is_active=True).select_related('student_group', 'teacher') if _student_can_play(game, request.user)]
    cards = {}
    for game in games:
        latest = BingoCard.objects.filter(student=request.user, game=game).order_by('-round_number').first()
        if latest:
            cards[game.id] = latest
    return render(request, 'student/bingo_game_list.html', {'games': games, 'cards': cards})


@login_required
def play_bingo(request, game_id):
    game = get_object_or_404(BingoGame.objects.select_related('student_group', 'teacher'), id=game_id, is_active=True)
    if not _student_can_play(game, request.user):
        messages.error(request, 'This Bingo game is not assigned to you.')
        return redirect('student_bingo_list')

    card = BingoCard.objects.filter(game=game, student=request.user).order_by('-round_number').first()

    if request.method == 'POST' and request.POST.get('action') == 'new_round':
        if card and card.has_bingo:
            card = _create_round(game, request.user)
            if card is None:
                messages.error(request, 'There are not enough matching learning materials for another round.')
        return redirect('play_bingo', game_id=game.id)

    # Returning later after a completed round always starts fresh automatically.
    if card is None or card.has_bingo and request.method == 'GET' and request.GET.get('finished') != '1':
        # Keep the completion prompt immediately after Bingo; dashboard/list links use ?finished=1 only to leave.
        if card is None:
            card = _create_round(game, request.user)

    if card is None:
        messages.error(request, 'This Bingo game does not currently have enough matching learning materials.')
        return redirect('student_bingo_list')

    if request.method == 'POST' and not card.has_bingo:
        action = request.POST.get('action')
        try:
            target_position = int(request.POST.get('target_position', '-1'))
        except (TypeError, ValueError):
            target_position = -1
        if 0 <= target_position < len(card.cells) and target_position not in card.marked_positions:
            card.moves_count += 1
            if action == 'listening_guess':
                try:
                    guessed_position = int(request.POST.get('position', '-1'))
                except (TypeError, ValueError):
                    guessed_position = -1
                if guessed_position == target_position:
                    card.marked_positions = sorted(card.marked_positions + [target_position])
                    card.correct_count += 1
                    messages.success(request, 'Correct! That square has been marked.')
                else:
                    card.incorrect_count += 1
                    messages.warning(request, 'Not quite. Listen again and try the next challenge.')
                _finish_attempt(card)
            elif action == 'sentence_submit':
                candidate = _normalize_sentence(request.POST.get('candidate', ''))
                answer = _normalize_sentence(card.cells[target_position].get('text', ''))
                if candidate == answer and answer:
                    card.marked_positions = sorted(card.marked_positions + [target_position])
                    card.correct_count += 1
                    messages.success(request, 'Correct sentence! The square has been marked.')
                else:
                    card.incorrect_count += 1
                    messages.warning(request, 'That order is not correct yet. Try another sentence challenge.')
                _finish_attempt(card)
        return redirect('play_bingo', game_id=game.id)

    unmarked = [i for i, cell in enumerate(card.cells) if not cell.get('free') and i not in card.marked_positions]
    target_position = random.choice(unmarked) if unmarked and not card.has_bingo else None
    challenge = card.cells[target_position] if target_position is not None else None
    sentence_tiles = []
    if game.game_mode == 'make_sentence' and challenge:
        sentence_tiles = list(_normalize_sentence(challenge.get('text', '')))
        if len(sentence_tiles) > 1:
            original = list(sentence_tiles)
            for _ in range(5):
                random.shuffle(sentence_tiles)
                if sentence_tiles != original:
                    break

    rows = []
    for row_index in range(game.card_size):
        row = []
        for col_index in range(game.card_size):
            position = row_index * game.card_size + col_index
            row.append({'position': position, 'cell': card.cells[position], 'marked': position in card.marked_positions})
        rows.append(row)

    return render(request, 'student/play_bingo.html', {'game': game, 'card': card, 'rows': rows, 'target_position': target_position, 'challenge': challenge, 'sentence_tiles': sentence_tiles})