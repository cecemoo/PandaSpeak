import random

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from teacher.bingo_models import BingoCard, BingoGame
from teacher.models import Idiom, Sentence, Vocabulary


def _eligible_materials(game):
    visibility_filter = Q(visibility='all') | Q(allowed_groups=game.student_group)
    level_filter = Q()
    if game.level != 'all':
        level_filter = Q(level=game.level) | Q(level='all')

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


def _generate_cells(game):
    pool = list(_eligible_materials(game))
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
        cells = _generate_cells(game)
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
        )

    if request.method == 'POST':
        try:
            position = int(request.POST.get('position', '-1'))
        except (TypeError, ValueError):
            position = -1

        if 0 <= position < len(card.cells) and not card.cells[position].get('free'):
            marked = list(card.marked_positions)
            if position in marked:
                marked.remove(position)
            else:
                marked.append(position)
            card.marked_positions = sorted(marked)
            card.has_bingo = _has_bingo(card)
            card.completed_at = timezone.now() if card.has_bingo else None
            card.save(update_fields=['marked_positions', 'has_bingo', 'completed_at', 'updated_at'])

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
