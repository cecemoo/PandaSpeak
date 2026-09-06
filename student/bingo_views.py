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
from teacher.bingo_models import BingoCard, BingoGame
from teacher.models import Idiom, Sentence, Vocabulary


LEVEL_ORDER = ['level1', 'level2', 'level3']


def _eligible_materials(game, level=None):
    visibility_filter = Q(visibility='all') | Q(allowed_groups=game.student_group)
    selected_level = level or game.level
    level_filter = Q()
    if selected_level != 'all':
        level_filter = Q(level=selected_level) | Q(level='all')

    if game.content_type == 'sentence':
        return Sentence.objects.filter(visibility_filter, level_filter).distinct()
    if game.content_type == 'expression':
        return Idiom.objects.filter(visibility_filter, level_filter).distinct()
    return Vocabulary.objects.filter(visibility_filter, level_filter).distinct()


def _serialize_item(game, item):
    if game.content_type == 'sentence':
        return {
            'id': item.id,
            'text': item.text,
            'pinyin': item.pinyin,
            'translation': item.translation,
            'free': False,
        }
    if game.content_type == 'expression':
        return {
            'id': item.id,
            'text': item.idiom,
            'pinyin': item.pinyin,
            'translation': item.english_translation,
            'free': False,
        }
    return {
        'id': item.id,
        'text': item.word,
        'pinyin': item.pinyin,
        'translation': item.english_translation,
        'free': False,
    }


def _generate_cells(game, level):
    pool = list(_eligible_materials(game, level))
    if len(pool) < game.required_item_count:
        return None

    selected = random.sample(pool, game.required_item_count)
    cells = [_serialize_item(game, item) for item in selected]

    if game.use_free_center and game.card_size % 2 == 1:
        center = (game.card_size * game.card_size) // 2
        cells.insert(center, {
            'id': None,
            'text': 'FREE',
            'pinyin': '自由格',
            'translation': 'Free Space',
            'free': True,
        })
    return cells


def _move_level(level, direction):
    if level not in LEVEL_ORDER:
        return level
    index = LEVEL_ORDER.index(level)
    new_index = max(0, min(len(LEVEL_ORDER) - 1, index + direction))
    return LEVEL_ORDER[new_index]


def _assigned_level_for_student(game, student):
    if not game.adaptive_difficulty:
        return game.level

    previous_cards = list(
        BingoCard.objects.filter(
            student=student,
            game__adaptive_difficulty=True,
            game__content_type=game.content_type,
            game__level=game.level,
        )
        .exclude(game=game)
        .select_related('game')
        .order_by('-created_at')[:8]
    )

    if previous_cards:
        base_level = previous_cards[0].assigned_level
    elif game.level in LEVEL_ORDER:
        base_level = game.level
    else:
        base_level = 'level1'

    evaluated = []
    for card in previous_cards:
        struggle_threshold = max(3, card.game.card_size * 2)
        if card.has_bingo or card.moves_count >= struggle_threshold:
            evaluated.append(card)
        if len(evaluated) == 3:
            break

    target_level = base_level
    if len(evaluated) >= 2:
        wins = sum(1 for card in evaluated if card.has_bingo)
        win_rate = wins / len(evaluated)
        if win_rate >= 0.67:
            target_level = _move_level(base_level, 1)
        elif win_rate <= 0.33:
            target_level = _move_level(base_level, -1)

    if _eligible_materials(game, target_level).count() >= game.required_item_count:
        return target_level

    if _eligible_materials(game, base_level).count() >= game.required_item_count:
        return base_level

    if game.level != 'all' and _eligible_materials(game, game.level).count() >= game.required_item_count:
        return game.level

    return 'all'


def _winning_positions(size):
    lines = []
    for row in range(size):
        lines.append([row * size + col for col in range(size)])
    for col in range(size):
        lines.append([row * size + col for row in range(size)])
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

    Notification.objects.create(
        user=teacher,
        title='Student Got Bingo!',
        message=f"{student_name} got Bingo in {card.game.title} at {card.assigned_level.replace('level', 'Level ')}.",
        link=teacher_link,
    )

    send_push_to_user(
        teacher,
        'Student Got Bingo!',
        f'{student_name} completed {card.game.title}.',
        teacher_link,
    )

    if teacher.email:
        send_mail(
            subject=f'PandaSpeak Bingo: {student_name} got Bingo!',
            message=(
                f"Hello {teacher.get_full_name() or teacher.email},\n\n"
                f"{student_name} got Bingo in '{card.game.title}'.\n"
                f"Difficulty: {card.assigned_level.replace('level', 'Level ')}\n\n"
                f"You can log in to PandaSpeak to review your Bingo activities.\n\n"
                f"Best regards,\n"
                f"PandaSpeak Support Team"
            ),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[teacher.email],
            fail_silently=True,
        )


@login_required
def bingo_game_list(request):
    games = BingoGame.objects.filter(
        is_active=True,
        student_group__students=request.user,
    ).select_related('student_group').distinct()

    cards = {
        card.game_id: card
        for card in BingoCard.objects.filter(student=request.user, game__in=games)
    }
    return render(request, 'student/bingo_game_list.html', {'games': games, 'cards': cards})


@login_required
def play_bingo(request, game_id):
    game = get_object_or_404(
        BingoGame,
        id=game_id,
        is_active=True,
        student_group__students=request.user,
    )

    card = BingoCard.objects.filter(game=game, student=request.user).first()
    if card is None:
        assigned_level = _assigned_level_for_student(game, request.user)
        cells = _generate_cells(game, assigned_level)
        if cells is None:
            messages.error(request, 'This Bingo game does not currently have enough matching learning materials.')
            return redirect('student_bingo_list')

        marked = []
        for position, cell in enumerate(cells):
            if cell.get('free'):
                marked.append(position)

        card = BingoCard.objects.create(
            game=game,
            student=request.user,
            cells=cells,
            marked_positions=marked,
            assigned_level=assigned_level,
        )

    if request.method == 'POST':
        try:
            position = int(request.POST.get('position', '-1'))
        except (TypeError, ValueError):
            position = -1

        if 0 <= position < len(card.cells) and not card.cells[position].get('free'):
            previously_had_bingo = card.has_bingo
            marked = list(card.marked_positions)
            if position in marked:
                marked.remove(position)
            else:
                marked.append(position)
            card.marked_positions = sorted(marked)
            card.moves_count += 1
            card.has_bingo = _has_bingo(card)
            card.completed_at = timezone.now() if card.has_bingo else None

            if card.has_bingo and not previously_had_bingo and not card.teacher_notified:
                _notify_teacher_of_bingo(card)
                card.teacher_notified = True

            card.save(update_fields=[
                'marked_positions',
                'moves_count',
                'has_bingo',
                'teacher_notified',
                'completed_at',
                'updated_at',
            ])

        return redirect('play_bingo', game_id=game.id)

    rows = []
    size = game.card_size
    for row_index in range(size):
        row = []
        for col_index in range(size):
            position = row_index * size + col_index
            row.append({
                'position': position,
                'cell': card.cells[position],
                'marked': position in card.marked_positions,
            })
        rows.append(row)

    return render(request, 'student/play_bingo.html', {
        'game': game,
        'card': card,
        'rows': rows,
    })
