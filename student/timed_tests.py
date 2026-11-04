"""Timed test completion shared by requests and scheduled expiry processing."""
from django.conf import settings
from django.core.mail import send_mail
from django.db import transaction
from django.db.models import Q
from django.utils import timezone
from account.models import CustomUser, Notification
from django.urls import reverse
from .models import (AssessmentRequest, TimedTestAttempt, StudentTestSubmission,
                     StudentListeningAnswer, StudentSpeakingAnswer)

SUPPORT_EMAIL = 'pandaspeaksupport@gmail.com'
SITE_ORIGIN = 'https://pandaspeak.org'


def is_manager_scored(test):
    """Whether a test's speaking part is scored by PandaSpeak managers.

    True for tests a manager created on the dashboard (is_manager_test)
    and for auto-generated assessment tests, which are linked from the
    fulfilled AssessmentRequest recorded when they were generated (see
    student.assessment).
    """
    return test.is_manager_test or AssessmentRequest.objects.filter(
        fulfilled_test=test).exists()


def manager_scored_q(prefix='test__'):
    """Q matching manager-scored tests (see is_manager_scored) inside a
    queryset filter; `prefix` is the lookup path to the LanguageTest
    (e.g. 'test__' from a submission, 'question__test__' from an answer).
    """
    return (
        Q(**{f'{prefix}is_manager_test': True})
        | Q(**{f'{prefix}assessment_requests__isnull': False})
    )


def notify_managers_speaking_submission(submission):
    """Alert PandaSpeak managers that a manager-scored test's speaking
    part is ready to score (Cece, 2026-11-03).

    No-op unless the submission's test is manager-scored (see
    is_manager_scored: manager-created tests and auto-generated
    assessment tests) with at least one speaking answer. Callers call
    this exactly once, when the submission is created, so no duplicate
    alerts go out: one email to the support inbox plus one Notification
    for every active staff/superuser user, both linking to the manager
    grading page for the submission.
    """
    test = submission.test
    if not is_manager_scored(test):
        return
    if not StudentSpeakingAnswer.objects.filter(submission=submission).exists():
        return
    student = submission.student
    student_name = student.get_full_name() or student.email
    grading_path = reverse('manager_grading_detail', args=[submission.id])
    send_mail(
        subject='Speaking test completed — ready to score',
        message=(
            f'{student_name} ({student.email}) has completed the test '
            f'"{test.title}".\n\n'
            f'The speaking part is ready to score:\n'
            f'{SITE_ORIGIN}{grading_path}\n'
        ),
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[SUPPORT_EMAIL],
        fail_silently=False,
    )
    managers = CustomUser.objects.filter(is_active=True).filter(
        Q(is_staff=True) | Q(is_superuser=True))
    for manager_user in managers:
        Notification.objects.create(
            user=manager_user,
            title='Speaking Test Ready to Score',
            message=(
                f'{student_name} completed "{test.title}". '
                f'The speaking part is ready to score.'
            ),
            link=grading_path,
        )


def finalize_attempt(attempt_id, auto=False):
    """Idempotently grade saved listening answers and attach saved recordings."""
    with transaction.atomic():
        attempt = TimedTestAttempt.objects.select_for_update().select_related('test', 'student').get(pk=attempt_id)
        existing = StudentTestSubmission.objects.filter(student=attempt.student, test=attempt.test).first()
        if existing:
            if not attempt.completed_at:
                attempt.completed_at = timezone.now()
                attempt.save(update_fields=['completed_at'])
            return existing
        if attempt.completed_at:
            return None
        now = timezone.now()
        expired = now >= attempt.deadline
        if expired:
            auto = True
        submission = StudentTestSubmission.objects.create(student=attempt.student, test=attempt.test, listening_score=0)
        score = 0
        for question in attempt.test.questions.all():
            if question.question_type in ('listen_mc', 'listen_text'):
                answer = (attempt.draft_answers or {}).get(f'answer_{question.pk}', '').strip()
                correct = answer.casefold() == (question.correct_answer or '').strip().casefold()
                earned = question.points if correct and answer else 0
                StudentListeningAnswer.objects.create(submission=submission, question=question, answer=answer, is_correct=correct, score=earned)
                score += earned
            elif question.question_type in ('speak_read', 'speaking_answer'):
                StudentSpeakingAnswer.objects.filter(
                    student=attempt.student, question=question, submission__isnull=True
                ).update(submission=submission)
        submission.listening_score = score
        submission.save(update_fields=['listening_score'])
        attempt.completed_at = now
        attempt.auto_submitted = auto
        attempt.save(update_fields=['completed_at', 'auto_submitted'])
        if attempt.test.teacher_id:
            Notification.objects.create(
                user=attempt.test.teacher, title='New Test Submission',
                message=f'{attempt.student.get_full_name() or attempt.student.email} submitted {attempt.test.title}.',
                link=reverse('teacher_student_test_results'),
            )
        notify_managers_speaking_submission(submission)
        return submission
