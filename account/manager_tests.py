"""Manager-created assessment tests (manager dashboard).

Cece's spec (2026-11-03): a manager can create a test for a specific
student — typically to fulfil a student's AssessmentRequest — or for all
users. The create form's audience control is a single dropdown ("All
users" or one student); on the edit page the audience becomes a checkbox
list so the manager can add more users (or switch back to All users).
Manager tests appear on the manager dashboard's Assessment Tests page,
where they can be edited, given questions, published, and deleted.

Publishing mirrors teacher.publish_test (email + Notification + push,
sender "PandaSpeak") and additionally fulfils any pending
AssessmentRequest linked to the test (the link is stored on the request
as fulfilled_test when the test is created from a request).

When a student completes a manager test that has speaking answers, the
managers are notified (see student.timed_tests
.notify_managers_speaking_submission) and score the speaking part on the
grading pages at the bottom of this module, mirroring the teacher
grading flow.
"""
from functools import wraps

from django import forms
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.http import require_POST

from student.models import (DEFAULT_TEST_TIME_LIMIT_MINUTES, AssessmentRequest,
                            LanguageTest, StudentSpeakingAnswer,
                            StudentTestSubmission, TestQuestion)
from teacher.forms import TestQuestionForm

from .announcement_views import manager
from .models import CustomUser, Notification
from .push import send_push_to_user

LEVEL_CHOICES = [('Level I', 'Level I'), ('Level II', 'Level II'), ('Level III', 'Level III')]


def manager_required(view):
    @wraps(view)
    @login_required(login_url='my_login')
    def wrapper(request, *args, **kwargs):
        if not manager(request.user):
            return redirect('home')
        return view(request, *args, **kwargs)
    return wrapper


def student_queryset():
    """Users a test can be assigned to: active students (not teachers/staff)."""
    return CustomUser.objects.filter(
        is_active=True, is_teacher=False, is_staff=False, is_superuser=False,
    ).order_by('email')


def student_label(user):
    name = user.get_full_name()
    return f'{name} ({user.email})' if name else user.email


class ManagerTestForm(forms.ModelForm):
    level = forms.ChoiceField(
        choices=LEVEL_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'}),
    )

    class Meta:
        model = LanguageTest
        fields = ['title', 'level', 'test_type', 'description',
                  'time_limit_minutes', 'available_from', 'available_until',
                  'is_active']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'test_type': forms.Select(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'time_limit_minutes': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'available_from': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}, format='%Y-%m-%dT%H:%M'),
            'available_until': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}, format='%Y-%m-%dT%H:%M'),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['available_from'].input_formats = ['%Y-%m-%dT%H:%M']
        self.fields['available_until'].input_formats = ['%Y-%m-%dT%H:%M']
        self.fields['time_limit_minutes'].help_text = (
            'Minutes each student has to finish the test. '
            f'Leave blank to use the {DEFAULT_TEST_TIME_LIMIT_MINUTES}-minute default.')

    def clean(self):
        cleaned_data = super().clean()
        available_from = cleaned_data.get('available_from')
        available_until = cleaned_data.get('available_until')
        if available_from and available_until and available_until <= available_from:
            self.add_error('available_until', 'Available until must be later than available from.')
        duration = cleaned_data.get('time_limit_minutes')
        if duration is not None and duration < 1:
            self.add_error('time_limit_minutes', 'Enter at least 1 minute.')
        return cleaned_data


class ManagerTestCreateForm(ManagerTestForm):
    """Create form: one audience dropdown — All users, or a single student."""
    audience = forms.ChoiceField(
        label='Assign to',
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'}),
        help_text='Choose "All users" to make the test available to every '
                  'student, or pick the student who requested it.',
    )
    request_id = forms.IntegerField(required=False, widget=forms.HiddenInput)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['audience'].choices = [('', 'All users')] + [
            (str(student.pk), student_label(student))
            for student in student_queryset()
        ]


class ManagerTestEditForm(ManagerTestForm):
    """Edit form: checkbox audience so the manager can add more users."""
    audience_all = forms.BooleanField(
        required=False, label='All users',
        help_text='Make the test available to every student (clears the '
                  'individual assignments below).')
    students = forms.ModelMultipleChoiceField(
        queryset=CustomUser.objects.none(), required=False,
        label='Assigned students',
        widget=forms.CheckboxSelectMultiple,
        help_text='Tick every student who should see this test.')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['students'].queryset = student_queryset()
        self.fields['students'].label_from_instance = student_label


def _linked_requests(test):
    return test.assessment_requests.select_related('student').order_by('-created_at')


@manager_required
def manager_test_list(request):
    pending_requests = (
        AssessmentRequest.objects.filter(status='pending')
        .select_related('student', 'fulfilled_test')
        .order_by('-created_at')
    )
    tests = (
        LanguageTest.objects.filter(is_manager_test=True)
        .order_by('-id')
        .prefetch_related('assigned_students', 'assessment_requests__student')
        .annotate(question_count=Count('questions'))
    )
    grading_waiting = StudentTestSubmission.objects.filter(
        test__is_manager_test=True,
        speaking_answers__score__isnull=True,
    ).distinct().count()
    context = {
        'pending_requests': pending_requests,
        'tests': tests,
        'grading_waiting': grading_waiting,
    }
    return render(request, 'account/manager_test_list.html', context)


@manager_required
def manager_create_test(request):
    assessment_request = None
    request_id = request.GET.get('request') or request.POST.get('request_id')
    if request_id:
        assessment_request = AssessmentRequest.objects.filter(
            id=request_id, status='pending').select_related('student').first()

    if request.method == 'POST':
        form = ManagerTestCreateForm(request.POST)
        if form.is_valid():
            test = form.save(commit=False)
            test.teacher = request.user if request.user.is_teacher else None
            test.is_manager_test = True
            test.is_published = False
            test.save()
            audience = form.cleaned_data.get('audience')
            if audience:
                test.assigned_students.set([int(audience)])
            if assessment_request is not None:
                assessment_request.fulfilled_test = test
                assessment_request.save(update_fields=['fulfilled_test', 'updated_at'])
            messages.success(request, 'Test created. Now add its questions.')
            return redirect('manager_test_questions', test_id=test.id)
    else:
        initial = {'time_limit_minutes': DEFAULT_TEST_TIME_LIMIT_MINUTES}
        if assessment_request is not None:
            level_label = assessment_request.get_level_display()
            type_label = assessment_request.get_test_type_display()
            initial.update({
                'title': f'{level_label} {type_label} Assessment',
                'level': level_label,
                'test_type': assessment_request.test_type,
                'audience': str(assessment_request.student_id),
                'request_id': assessment_request.id,
            })
        form = ManagerTestCreateForm(initial=initial)
    context = {
        'form': form,
        'assessment_request': assessment_request,
        'heading': 'Create Assessment Test',
        'submit_label': 'Create Test',
    }
    return render(request, 'account/manager_test_form.html', context)


@manager_required
def manager_edit_test(request, test_id):
    test = get_object_or_404(LanguageTest, id=test_id, is_manager_test=True)
    if request.method == 'POST':
        form = ManagerTestEditForm(request.POST, instance=test)
        if form.is_valid():
            form.save()
            if form.cleaned_data.get('audience_all'):
                test.assigned_students.clear()
            else:
                test.assigned_students.set(form.cleaned_data.get('students'))
            messages.success(request, 'Test updated successfully.')
            return redirect('manager_test_list')
    else:
        form = ManagerTestEditForm(instance=test, initial={
            'audience_all': not test.assigned_students.exists(),
            'students': test.assigned_students.all(),
        })
    context = {
        'form': form,
        'test': test,
        'linked_requests': _linked_requests(test),
        'heading': f'Edit Test: {test.title}',
        'submit_label': 'Save Changes',
    }
    return render(request, 'account/manager_test_form.html', context)


@manager_required
def manager_test_questions(request, test_id):
    test = get_object_or_404(LanguageTest, id=test_id, is_manager_test=True)
    if request.method == 'POST':
        form = TestQuestionForm(request.POST, request.FILES)
        if form.is_valid():
            question = form.save(commit=False)
            question.test = test
            question.correct_answer = request.POST.get('correct_choice') or request.POST.get('correct_answer')
            question.save()
            messages.success(request, 'Question added successfully.')
            return redirect('manager_test_questions', test_id=test.id)
    else:
        form = TestQuestionForm()
    questions = TestQuestion.objects.filter(test=test).order_by('order')
    context = {
        'form': form,
        'test': test,
        'questions': questions,
        'linked_requests': _linked_requests(test),
    }
    return render(request, 'account/manager_test_questions.html', context)


@manager_required
@require_POST
def manager_delete_test_question(request, test_id, question_id):
    test = get_object_or_404(LanguageTest, id=test_id, is_manager_test=True)
    question = get_object_or_404(TestQuestion, id=question_id, test=test)
    question.delete()
    messages.success(request, 'Question deleted.')
    return redirect('manager_test_questions', test_id=test.id)


@manager_required
@require_POST
def manager_publish_test(request, test_id):
    test = get_object_or_404(LanguageTest, id=test_id, is_manager_test=True)
    if not test.questions.exists():
        messages.error(request, 'Please add at least one question before publishing the test.')
        return redirect('manager_test_questions', test_id=test.id)
    test.is_published = True
    test.save()
    if not test.notification_sent:
        assigned = list(test.assigned_students.filter(is_active=True))
        if assigned:
            students = assigned
        else:
            students = CustomUser.objects.filter(
                is_teacher=False,
                is_active=True,
                is_staff=False,
            )
        for student in students:
            if student.email:
                send_mail(
                    subject=f'New PandaSpeak Test: {test.title}',
                    message=(
                        f'Hello {student.get_full_name() or student.email},\n\n'
                        f"A new test '{test.title}' has been published by PandaSpeak.\n\n"
                        f'Please log into PandaSpeak to take the test.\n\n'
                        f'Best regards,\n'
                        f'PandaSpeak'
                    ),
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[student.email],
                    fail_silently=False,
                )
            Notification.objects.create(
                user=student,
                title='New Test Available',
                message=f'{test.title} has been published by PandaSpeak. Select View to take the test.',
                link=reverse('take_test', args=[test.id]),
            )
            send_push_to_user(
                student,
                'New Test Available',
                test.title,
                '/student/student_dashboard/'
            )
        test.notification_sent = True
        test.save()
    fulfilled = 0
    for assessment_request in AssessmentRequest.objects.filter(
            fulfilled_test=test, status='pending'):
        assessment_request.status = 'fulfilled'
        assessment_request.save(update_fields=['status', 'updated_at'])
        fulfilled += 1
    if fulfilled:
        messages.success(
            request,
            f'Test published and {fulfilled} assessment request(s) marked fulfilled.')
    else:
        messages.success(request, 'Test published successfully.')
    return redirect('manager_test_list')


@manager_required
def manager_delete_test(request, test_id):
    test = get_object_or_404(LanguageTest, id=test_id, is_manager_test=True)
    if request.method == 'POST':
        test.delete()
        messages.success(request, 'Test deleted successfully.')
        return redirect('manager_test_list')
    context = {
        'test': test,
        'question_count': test.questions.count(),
    }
    return render(request, 'account/manager_delete_test.html', context)


# ---------------------------------------------------------------------------
# Speaking grading (Cece, 2026-11-03: when a student completes a speaking
# test, the manager is notified and scores the speaking part). Mirrors the
# teacher grading flow (teacher.views.grade_speaking_answer), scoped to
# manager tests.
# ---------------------------------------------------------------------------

@manager_required
def manager_grading_list(request):
    submissions = (
        StudentTestSubmission.objects.filter(
            test__is_manager_test=True, speaking_answers__isnull=False)
        .select_related('student', 'test')
        .annotate(
            speaking_total=Count('speaking_answers', distinct=True),
            speaking_graded=Count(
                'speaking_answers',
                filter=Q(speaking_answers__score__isnull=False),
                distinct=True),
        )
        .order_by('-submitted_at')
        .distinct()
    )
    context = {'submissions': submissions}
    return render(request, 'account/manager_grading_list.html', context)


@manager_required
def manager_grading_detail(request, submission_id):
    submission = get_object_or_404(
        StudentTestSubmission, id=submission_id, test__is_manager_test=True)
    speaking_answers = (
        submission.speaking_answers.select_related('question')
        .order_by('question__order')
    )
    context = {
        'submission': submission,
        'speaking_answers': speaking_answers,
    }
    return render(request, 'account/manager_grading_detail.html', context)


@manager_required
@require_POST
def manager_grade_speaking_answer(request, answer_id):
    answer = get_object_or_404(
        StudentSpeakingAnswer,
        id=answer_id,
        question__test__is_manager_test=True,
        submission__isnull=False,
    )
    submission = answer.submission
    score = request.POST.get('score')
    teacher_feedback = request.POST.get('teacher_feedback', '')
    try:
        score = float(score)
        if score < 0 or score > answer.question.points:
            messages.error(
                request,
                f'Score must be between 0 and {answer.question.points}.'
            )
            return redirect('manager_grading_detail', submission_id=submission.id)
    except (TypeError, ValueError):
        messages.error(request, 'Please enter a valid score.')
        return redirect('manager_grading_detail', submission_id=submission.id)

    answer.score = score
    answer.teacher_feedback = teacher_feedback
    answer.save(update_fields=['score', 'teacher_feedback'])
    # Delete audio file after grading to save storage space (as teachers do).
    if answer.audio_file:
        answer.audio_file.delete(save=False)
        answer.audio_file = None
        answer.save(update_fields=['audio_file'])

    was_already_graded = submission.is_graded
    speaking_answers = submission.speaking_answers.all()
    speaking_score = sum(
        speaking_answer.score or 0
        for speaking_answer in speaking_answers
    )
    submission.speaking_score = speaking_score
    all_speaking_graded = all(
        speaking_answer.score is not None
        for speaking_answer in speaking_answers
    )
    if all_speaking_graded:
        submission.total_score = (
            (submission.listening_score or 0)
            + (submission.speaking_score or 0)
        )
        submission.is_graded = True
        submission.save(update_fields=['speaking_score', 'total_score', 'is_graded'])
        result_link = reverse(
            'test_result',
            kwargs={'submission_id': submission.id}
        )
        Notification.objects.update_or_create(
            user=submission.student,
            title='Test Graded',
            link=result_link,
            defaults={
                'message': (
                    f'Your test "{submission.test.title}" has been graded. '
                    f'Your total score is {submission.total_score}.'
                ),
                'is_read': False,
            }
        )
        if not was_already_graded:
            send_push_to_user(
                submission.student,
                'Test Graded',
                f'Your results for {submission.test.title} are ready.',
                '/student/test-results/'
            )
    else:
        submission.save(update_fields=['speaking_score'])
    messages.success(request, f'Question {answer.question.order} grade saved.')
    return redirect('manager_grading_detail', submission_id=submission.id)
