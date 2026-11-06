"""Automatic subscription-renewal feedback survey (Cece, 2026-11-05).

When a student's base subscription period ends in 7 days, the existing
send_subscription_reminders command also invites them to a short survey.
The survey is a single system-owned LearningSurvey (flagged
is_system_renewal); answers are reviewed by the PandaSpeak managers on
the manager dashboard's Renewal Survey page — they never go to a
teacher. Invites are tracked by RenewalSurveyInvite, unique per
(user, period_end), so a student is invited at most once per period.
"""
from django.conf import settings
from django.core.mail import send_mail
from django.urls import reverse
from django.utils import timezone

from account.models import CustomUser, Notification
from account.push import send_push_to_user
from teacher.models import LearningSurvey, SurveyQuestion

from .models import RenewalSurveyInvite

SURVEY_TITLE = 'PandaSpeak Subscription Renewal Survey'
SURVEY_DESCRIPTION = (
    'Your subscription period ends soon. Please take a minute to tell us '
    'how your learning went — your answers go to the PandaSpeak team.'
)
SUPPORT_EMAIL = 'pandaspeaksupport@gmail.com'
SITE_ORIGIN = 'https://pandaspeak.org'
INVITE_TITLE = 'A Quick Survey Before Your Subscription Renews'

QUESTIONS = [
    # (question_type, question_text, option_a, option_b, option_c, option_d)
    ('rating', 'Overall, how satisfied are you with PandaSpeak?', None, None, None, None),
    ('multiple_choice', 'How likely are you to renew your subscription?',
     'Very likely', 'Likely', 'Not sure', 'Unlikely'),
    ('multiple_choice', 'What did you use most this year?',
     'Learning materials (vocabulary, sentences, expressions)',
     'Chinese history lessons',
     'Games, flashcards and tests',
     'Tutoring or AI conversation practice'),
    ('rating', 'How would you rate the quality of the learning materials?', None, None, None, None),
    ('text', 'What should PandaSpeak improve or add next?', None, None, None, None),
    ('text', 'Anything else you would like to tell us?', None, None, None, None),
]


def _survey_owner():
    """The account that owns the system survey: first superuser, else
    first staff user, else None (no survey can be offered)."""
    return (
        CustomUser.objects.filter(is_superuser=True).order_by('id').first()
        or CustomUser.objects.filter(is_staff=True).order_by('id').first()
    )


def get_or_create_renewal_survey():
    """Return the canonical system renewal survey, creating it (with its
    six questions) on first use. Returns None when no superuser/staff
    account exists to own it."""
    survey = LearningSurvey.objects.filter(is_system_renewal=True).order_by('id').first()
    if survey is not None:
        return survey
    owner = _survey_owner()
    if owner is None:
        return None
    survey = LearningSurvey.objects.create(
        teacher=owner,
        title=SURVEY_TITLE,
        description=SURVEY_DESCRIPTION,
        is_active=True,
        is_system_renewal=True,
        student_group=None,
        published_at=timezone.now(),
        availability_days=36500,
    )
    for order, (qtype, text, a, b, c, d) in enumerate(QUESTIONS, start=1):
        SurveyQuestion.objects.create(
            survey=survey,
            question_text=text,
            question_type=qtype,
            option_a=a,
            option_b=b,
            option_c=c,
            option_d=d,
            order=order,
        )
    return survey


def send_renewal_survey_invite(user, subscription):
    """Invite `user` to the renewal survey for the period ending at
    subscription.access_until. Returns True only when a NEW invite was
    created and the student was notified (notification + push + email)."""
    if not subscription.access_until:
        return False
    invite, created = RenewalSurveyInvite.objects.get_or_create(
        user=user,
        period_end=subscription.access_until,
        defaults={'subscription': subscription},
    )
    if not created:
        return False
    survey = get_or_create_renewal_survey()
    if survey is None:
        return False

    period_end = subscription.access_until
    link = reverse('take_learning_survey', args=[survey.id])
    message = (
        f'Your PandaSpeak subscription period ends on {period_end:%b %d, %Y}. '
        'Please take a minute to complete our short survey and tell us how '
        'your learning went — your answers go to the PandaSpeak team.'
    )
    Notification.objects.create(user=user, title=INVITE_TITLE, message=message, link=link)
    send_push_to_user(user, INVITE_TITLE, message, link)
    if user.email:
        greeting = f'Hello {user.first_name or "PandaSpeak learner"},\n\n'
        body = (
            f'Your PandaSpeak subscription period ends on {period_end:%b %d, %Y}. '
            'Before it does, we would love to hear how your learning went. '
            'Please take a minute to complete our short renewal survey:\n\n'
            f'{SITE_ORIGIN}{link}\n\n'
            'Your answers go to the PandaSpeak team and help us improve.'
        )
        footer = '\n\nBest regards,\nPandaSpeak Team'
        send_mail(INVITE_TITLE, greeting + body + footer, settings.DEFAULT_FROM_EMAIL, [user.email], fail_silently=True)
    return True


def notify_managers_renewal_survey_response(student, response):
    """Tell the PandaSpeak managers a renewal survey was submitted: one
    email to the support inbox plus a Notification for every active
    staff/superuser user, linking to the manager responses page. Mirrors
    student.timed_tests.notify_managers_speaking_submission."""
    from django.db.models import Q

    student_name = student.get_full_name() or student.email
    responses_path = reverse('manager_renewal_survey_responses')
    send_mail(
        subject=f'New Renewal Survey Response: {student_name}',
        message=(
            f'{student_name} ({student.email}) has completed the '
            f'PandaSpeak subscription renewal survey.\n\n'
            f'Review renewal survey responses:\n'
            f'{SITE_ORIGIN}{responses_path}\n'
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
            title='New Renewal Survey Response',
            message=f'{student_name} submitted the subscription renewal survey.',
            link=responses_path,
        )
