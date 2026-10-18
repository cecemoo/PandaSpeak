"""Timed test completion shared by requests and scheduled expiry processing."""
from django.db import transaction
from django.utils import timezone
from account.models import Notification
from django.urls import reverse
from .models import (TimedTestAttempt, StudentTestSubmission, StudentListeningAnswer,
                     StudentSpeakingAnswer)


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
        if not auto and expired:
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
        return submission
