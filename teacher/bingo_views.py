from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from account.models import CustomUser, Notification
from account.push import send_push_to_user
from course.models import StudentGroup

from .bingo_forms import BingoGameForm
from .bingo_models import BingoGame
from .models import Idiom, Sentence, Vocabulary


def _audience_students(game):
    if game.audience == 'subscribers':
        return CustomUser.objects.filter(
            is_active=True,
            is_teacher=False,
            is_staff=False,
            subscription__is_active=True,
        ).distinct()

    if game.audience == 'my_students':
        return CustomUser.objects.filter(
            is_active=True,
            groups_joined__teacher=game.teacher,
            groups_joined__is_active=True,
        ).distinct()

    if game.student_group:
        return game.student_group.students.filter(is_active=True).distinct()

    return CustomUser.objects.none()


def _visibility_filter_for_game(game):
    if game.audience == 'subscribers':
        return Q(visibility='all')

    if game.audience == 'my_students':
        teacher_groups = StudentGroup.objects.filter(
            teacher=game.teacher,
            is_active=True,
        )
        return Q(visibility='all') | Q(allowed_groups__in=teacher_groups)

    if game.student_group:
        return Q(visibility='all') | Q(allowed_groups=game.student_group)

    return Q(visibility='all')


def _category_id_for_game(game, expected_prefix):
    if not game.category_key:
        return None
    prefix, separator, raw_id = game.category_key.partition(':')
    if separator != ':' or prefix != expected_prefix:
        return None
    try:
        return int(raw_id)
    except (TypeError, ValueError):
        return None


def _eligible_materials(game):
    visibility_filter = _visibility_filter_for_game(game)
    level_filter = Q()
    if game.level != 'all':
        level_filter = Q(level=game.level) | Q(level='all')

    if game.game_mode == 'make_sentence':
        queryset = Sentence.objects.filter(visibility_filter, level_filter)
        category_id = _category_id_for_game(game, 'sentence')
        if category_id:
            queryset = queryset.filter(category_id=category_id)
        return queryset.distinct()

    if game.content_type == 'sentence':
        queryset = (
            Sentence.objects
            .filter(visibility_filter, level_filter, audio_file__isnull=False)
            .exclude(audio_file='')
        )
        category_id = _category_id_for_game(game, 'sentence')
        if category_id:
            queryset = queryset.filter(category_id=category_id)
        return queryset.distinct()

    if game.content_type == 'expression':
        queryset = (
            Idiom.objects
            .filter(visibility_filter, level_filter, audio_scenario_file__isnull=False)
            .exclude(audio_scenario_file='')
        )
        category_id = _category_id_for_game(game, 'expression')
        if category_id:
            queryset = queryset.filter(category_id=category_id)
        return queryset.distinct()

    queryset = (
        Vocabulary.objects
        .filter(visibility_filter, level_filter, audio_file__isnull=False)
        .exclude(audio_file='')
    )
    category_id = _category_id_for_game(game, 'vocabulary')
    if category_id:
        queryset = queryset.filter(category_id=category_id)
    return queryset.distinct()


def _notify_students_about_bingo(game):
    students = _audience_students(game)
    play_link = reverse('play_bingo', args=[game.id])
    mode_name = game.get_game_mode_display()

    for student in students:
        Notification.objects.create(
            user=student,
            title=f'New {mode_name} Available',
            message=f"{game.title} is ready to play. Practice your Chinese and try to get Bingo!",
            link=play_link,
        )

        send_push_to_user(
            student,
            f'New {mode_name} Available',
            game.title,
            play_link,
        )

        if student.email:
            send_mail(
                subject=f'New PandaSpeak {mode_name}: {game.title}',
                message=(
                    f"Hello {student.get_full_name() or student.email},\n\n"
                    f"A new {mode_name}, '{game.title}', is now available on PandaSpeak.\n\n"
                    f"Log in to PandaSpeak to play and practice your Chinese.\n\n"
                    f"Best regards,\n"
                    f"PandaSpeak Support Team"
                ),
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[student.email],
                fail_silently=True,
            )


@login_required
def create_bingo_game(request):
    if request.method == 'POST':
        form = BingoGameForm(request.POST, teacher=request.user)
        if form.is_valid():
            game = form.save(commit=False)
            game.teacher = request.user
            if game.game_mode == 'make_sentence':
                game.content_type = 'sentence'

            minimum_required = 8 if game.use_free_center else 9
            available = _eligible_materials(game).count()

            if available < minimum_required:
                if game.game_mode == 'listening':
                    detail = 'matching items with audio'
                else:
                    detail = 'matching sentences'
                form.add_error(
                    None,
                    f'Bingo needs at least {minimum_required} {detail} for a 3 x 3 game, but only {available} are currently available. '
                    'Choose another category or level, or add more learning materials.'
                )
            else:
                game.save()
                if game.is_active:
                    _notify_students_about_bingo(game)
                    messages.success(
                        request,
                        'Bingo game created. Students can choose 3 x 3, 4 x 4, or 5 x 5 when enough matching materials are available.'
                    )
                else:
                    messages.success(
                        request,
                        'Bingo game saved as inactive. Students were not notified yet.'
                    )
                return redirect('teacher_bingo_list')
    else:
        form = BingoGameForm(teacher=request.user)

    return render(request, 'teacher/create_bingo_game.html', {'form': form})


@login_required
def bingo_game_list(request):
    games = BingoGame.objects.filter(teacher=request.user).select_related('student_group')
    return render(request, 'teacher/bingo_game_list.html', {'games': games})


@login_required
def delete_bingo_game(request, game_id):
    game = get_object_or_404(BingoGame, id=game_id, teacher=request.user)
    if request.method == 'POST':
        game.delete()
        messages.success(request, 'Bingo game deleted.')
    return redirect('teacher_bingo_list')
