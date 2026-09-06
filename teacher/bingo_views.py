from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from account.models import Notification
from account.push import send_push_to_user

from .bingo_forms import BingoGameForm
from .bingo_models import BingoGame
from .models import Idiom, Sentence, Vocabulary


def _eligible_materials(content_type, level, group):
    visibility_filter = Q(visibility='all') | Q(allowed_groups=group)
    level_filter = Q()
    if level != 'all':
        level_filter = Q(level=level) | Q(level='all')

    if content_type == 'sentence':
        return Sentence.objects.filter(visibility_filter, level_filter).distinct()
    if content_type == 'expression':
        return Idiom.objects.filter(visibility_filter, level_filter).distinct()
    return Vocabulary.objects.filter(visibility_filter, level_filter).distinct()


def _notify_students_about_bingo(game):
    students = game.student_group.students.filter(is_active=True)
    play_link = reverse('play_bingo', args=[game.id])

    for student in students:
        Notification.objects.create(
            user=student,
            title='New Chinese Bingo Available',
            message=f"{game.title} is ready to play. Practice your Chinese and try to get Bingo!",
            link=play_link,
        )

        send_push_to_user(
            student,
            'New Chinese Bingo Available',
            game.title,
            play_link,
        )

        if student.email:
            send_mail(
                subject=f'New PandaSpeak Chinese Bingo: {game.title}',
                message=(
                    f"Hello {student.get_full_name() or student.email},\n\n"
                    f"A new Chinese Bingo game, '{game.title}', is now available on PandaSpeak.\n\n"
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

            required = game.required_item_count
            available = _eligible_materials(
                game.content_type,
                game.level,
                game.student_group,
            ).count()

            if available < required:
                form.add_error(
                    'card_size',
                    f'This card needs {required} matching items, but only {available} are currently available. '
                    'Choose a smaller card, another level/content type, or add more learning materials.'
                )
            else:
                game.save()
                _notify_students_about_bingo(game)
                messages.success(
                    request,
                    'Bingo game created. Students in the selected group were notified by PandaSpeak and email.'
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
