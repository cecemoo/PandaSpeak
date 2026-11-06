"""Manager view of the automatic subscription-renewal survey responses.

Cece's spec (2026-11-05): students whose base subscription period ends
in 7 days are automatically invited to a short feedback survey (see
subscription.renewal_survey); the answers come back to the PandaSpeak
managers. This page lists every response to the system renewal survey,
newest first, with each question and the student's answer.
"""
from django.shortcuts import render

from subscription.models import RenewalSurveyInvite
from teacher.models import LearningSurvey, SurveyResponse

from .manager_tests import manager_required


@manager_required
def manager_renewal_survey_responses(request):
    survey = LearningSurvey.objects.filter(
        is_system_renewal=True).order_by('id').first()
    entries = []
    if survey is not None:
        responses = (
            SurveyResponse.objects.filter(survey=survey)
            .select_related('student')
            .prefetch_related('answers__question')
            .order_by('-submitted_at')
        )
        # Latest invite per student carries the period end the survey
        # was about (an invite is unique per user + period end).
        invites = {}
        for invite in RenewalSurveyInvite.objects.filter(
                user__in=[r.student_id for r in responses]).order_by('-sent_at'):
            invites.setdefault(invite.user_id, invite)
        for response in responses:
            answers = sorted(
                response.answers.all(),
                key=lambda answer: answer.question.order,
            )
            invite = invites.get(response.student_id)
            entries.append({
                'response': response,
                'student_name': response.student.get_full_name() or response.student.email,
                'student_email': response.student.email,
                'submitted_at': response.submitted_at,
                'period_end': invite.period_end if invite else None,
                'answers': answers,
            })
    return render(request, 'account/manager_renewal_survey_responses.html', {
        'survey': survey,
        'entries': entries,
        'response_count': len(entries),
    })
