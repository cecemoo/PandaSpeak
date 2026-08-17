from multiprocessing import context
from django.shortcuts import redirect, render, get_object_or_404
from django.contrib.auth.decorators import login_required
from subscription.models import Subscription
from subscription.decorators import subscription_required
from teacher.models import Vocabulary, Sentence, Pronunciation, Idiom, Tone, VocabularyCategory, SentenceCategory, IdiomCategory, LearningSurvey, SurveyResponse
from datetime import date
from django.http import JsonResponse
from django.core.mail import EmailMessage
from django.conf import settings
from django.utils import timezone
from .models import LanguageTest, TestQuestion, StudentSpeakingAnswer, StudentTestSubmission, StudentListeningAnswer, StudentSpeakingAnswer
from teacher.models import LearningSurvey, SurveyResponse, SurveyAnswer
from django.contrib import messages
from django.core.mail import send_mail




@login_required(login_url='my_login')
def student_dashboard(request):
    has_subscription = Subscription.objects.filter(
        user=request.user,
        is_active=True
    ).exists()
    sub = Subscription.objects.filter(
        user=request.user,
        is_active=True
    ).first()
    available_surveys = LearningSurvey.objects.filter(
        is_active=True
    ).exclude(
        responses__student=request.user
    )
    context = {
        'has_subscription': sub is not None,
        'SubPlan': sub.subscription_plan if sub else 'No Active Subscription',
        'available_surveys': available_surveys
    }
    return render(request, 'student/student_dashboard.html', context)



@login_required(login_url='my_login')
def access_learning_materials(request):
    has_subscription = Subscription.objects.filter(
        user=request.user,
        is_active=True
    ).first()

    if not has_subscription:
        return redirect('subscription_plans')
    
    vocabulary_categories = VocabularyCategory.objects.prefetch_related('vocabularies').all()
    sentence_categories = SentenceCategory.objects.prefetch_related('sentences').all()
    idiom_categories = IdiomCategory.objects.prefetch_related('idioms').all()
    context = {
        'vocabulary_categories': vocabulary_categories,
        'sentence_categories': sentence_categories,
        'idiom_categories': idiom_categories,
    }
    return render(request, 'student/access_learning_materials.html', context)



@login_required(login_url='my_login')
@subscription_required
def vocabulary_category_page(request, category_id):
    category = VocabularyCategory.objects.get(id=category_id)
    vocabularies = Vocabulary.objects.filter(category=category)
    return render(request, 'student/vocabulary_page.html', {'category': category, 'vocabularies': vocabularies})



@login_required(login_url='my_login')
@subscription_required
def pronunciation_page(request):
    pronunciations = Pronunciation.objects.all()
    base_sets = list(
        Tone.objects.values_list('base_pinyin', flat=True)
        .distinct()
        .order_by('base_pinyin')
    )
    tones = []
    today = date.today().isoformat()
    if base_sets:
        if request.session.get('tone_date') != today:
            index = date.today().toordinal() % len(base_sets)
            request.session['tone_date'] = today
            request.session['today_base'] = base_sets[index]
            
        today_base = request.session.get('today_base')
        tones = Tone.objects.filter(base_pinyin=today_base).order_by('id')
    return render(request, 'student/pronunciation_page.html', {'pronunciations': pronunciations, 'tones': tones})



@login_required(login_url='my_login')
@subscription_required
def sentence_category_page(request, category_id):
    category = SentenceCategory.objects.get(id=category_id)
    sentences = Sentence.objects.filter(category=category)
    return render(request, 'student/sentence_page.html', {'category': category, 'sentences': sentences})


   

@login_required(login_url='my_login')
@subscription_required
def idiom_category_page(request, category_id):
    category = IdiomCategory.objects.get(id=category_id)
    idioms = Idiom.objects.filter(category=category)
    return render(request, 'student/idiom_page.html', {'category': category, 'idioms': idioms})
   



@login_required(login_url='my_login')
def subscription_plans(request):
    return render(request, 'student/subscription_plans.html')


@login_required(login_url='my_login')
def account_management(request):
    sub = Subscription.objects.filter( user=request.user, is_active=True).first()
    context = {
        "has_subscription": sub is not None,
        "SubPlan": sub.subscription_plan if sub else 'No Active Subscription',
        "is_cancelled": sub.is_cancelled if sub else False,
        "access_until": sub.access_until if sub else None,
    }
    return render(request, 'student/account_management.html', context)



@login_required(login_url='my_login')
def subscription_locked(request):
    return render(request, 'student/subscription_locked.html')



@login_required(login_url='my_login')
def test_list(request):
    completed_test_ids = StudentTestSubmission.objects.filter(
        student=request.user
    ).values_list('test_id', flat=True)
    tests = LanguageTest.objects.filter(is_active=True, is_published=True).exclude(id__in=completed_test_ids)
    context = {
        'tests': tests
    }
    return render(request, 'student/test_list.html', context)


@login_required(login_url='my_login')
def take_test(request, test_id):
            test = get_object_or_404(
                LanguageTest,
                id=test_id,
                is_active=True,
                is_published=True
            )
            questions = TestQuestion.objects.filter(
                test=test
            ).order_by('order')
            if request.method == 'POST':
                submission = StudentTestSubmission.objects.create(
                    student=request.user,
                    test=test,
                    listening_score=0
                )
                listening_score = 0
                listening_total = 0
                speaking_recordings = []
                for question in questions:
                    # -------------------------
                    # LISTENING QUESTIONS
                    # -------------------------
                    if question.question_type in [
                        'listen_mc',
                        'listen_text'
                    ]:
                        listening_total += question.points
                        student_answer = request.POST.get(
                            f'answer_{question.id}',
                            ''
                        ).strip()
                        correct_answer = (
                            question.correct_answer or ''
                        ).strip()
                        is_correct = (
                            student_answer.casefold()
                            == correct_answer.casefold()
                        )
                        earned_score = (
                            question.points if is_correct else 0
                        )
                        listening_score += earned_score
                        StudentListeningAnswer.objects.create(
                            submission=submission,
                            question=question,
                            answer=student_answer,
                            is_correct=is_correct,
                            score=earned_score
                        )
                    # -------------------------
                    # SPEAKING QUESTIONS
                    # -------------------------
                    elif question.question_type in [
                        'speak_read',
                        'speaking_answer'
                    ]:
                        recording = request.FILES.get(
                            f'recording_{question.id}'
                        )
                        if recording:
                            StudentSpeakingAnswer.objects.create(
                                student=request.user,
                                question=question
                            )
                            speaking_recordings.append(
                                (question, recording)
                            )
                submission.listening_score = listening_score
                submission.save(
                    update_fields=['listening_score']
                )
                # -------------------------
                # EMAIL SPEAKING RECORDINGS
                # -------------------------
                if speaking_recordings:
                    teacher = test.teacher
                    student_name = request.user.get_full_name()
                    if not student_name:
                        student_name = request.user.email
                    email = EmailMessage(
                        subject=f'PandaSpeak Test Submission - {test.title}',
                        body=f"""
        Student: {student_name}
        Student Email: {request.user.email}
        Test: {test.title}
        Listening Score:
        {listening_score} / {listening_total}
        The student's speaking recordings are attached.
        Please review and grade the speaking portion.
        """,
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        to=[teacher.email],
                    )
                    for question, recording in speaking_recordings:
                        recording.seek(0)
                        email.attach(
                            f'question_{question.order}_{recording.name}',
                            recording.read(),
                            recording.content_type
                        )
                    email.send(fail_silently=False)
                    # Mark speaking answers as emailed
                    StudentSpeakingAnswer.objects.filter(
                        student=request.user,
                        question__test=test,
                        email_sent=False
                    ).update(
                        email_sent=True
                    )
                return render(
                    request,
                    'student/test_result.html',
                    {
                        'test': test,
                        'listening_score': listening_score,
                        'listening_total': listening_total,
                        'has_speaking': bool(speaking_recordings),
                    }
                )
            return render(
                request,
                'student/take_test.html',
                {
                    'test': test,
                    'questions': questions,
                }
            )





@login_required(login_url='my_login')
def submit_speaking_answer(request, question_id):
    if request.method != 'POST':
        return JsonResponse({
            'success': False,
            'message': 'Invalid request method.'
        }, status=400)
    question = get_object_or_404(TestQuestion, id=question_id)
    if question.question_type not in [
        'speak_read',
        'speaking_answer'
    ]:
        return JsonResponse({
            'success': False,
            'message': 'No recording was received.'
        }, status=400)

    answer = StudentSpeakingAnswer.objects.create(
        student=request.user,
        question=question
    )
    try:
        student_name = request.user.get_full_name()
        if not student_name:
            student_name = request.user.username
        subject = (
            f'PandaSpeak Speaking Test - '
            f'{question.test.title} - '
            f'{student_name}'
        )
        message = f"""
        A student submitted a PandaSpeak speaking test recording.
        Student: {student_name}
        Username: {request.user.username}
        Test: {question.test.title}
        Question: {question.order}

        Question: {question.prompt}
        Submitted: {answer.submitted_at}

        The student's audio recording is attached to this email.
        """
        email = EmailMessage(
            subject=subject,
            body=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[teacher_email],
        )
        email.attach(
            answer.audio_file.name,
            answer.audio_file.read(),
            answer.audio_file.content_type
        )
        email.send(fail_silently=False)
        answer.email_sent = True
        answer.email_sent_at = timezone.now()
        answer.save(
            update_fields=[
                'email_sent',
                'email_sent_at'
            ]
        )
        return JsonResponse({
            'success': True,
            'message': 'Your recording has been submitted successfully.'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'An error occurred while sending the email: {str(e)}'
        }, status=500)




@login_required(login_url='my_login')
def test_result(request, submission_id):
    submission = get_object_or_404(
        StudentTestSubmission,
        id=submission_id,
        student=request.user
    )
    context = {
        'test': submission.test,
        'submission': submission,
    }
    return render(request, 'student/test_result.html', context)


@login_required(login_url='my_login')
def student_test_results(request):
    results = StudentTestSubmission.objects.filter(
        student=request.user
    ).select_related('test').order_by('-submitted_at')
    return render(request, 'student/student_test_results.html', {'results': results})






@login_required(login_url='my_login')
def take_learning_survey(request, survey_id):

    survey = get_object_or_404(
    LearningSurvey,
    id=survey_id,
    is_active=True
    )

    # Prevent duplicate submission
    if SurveyResponse.objects.filter(
        survey=survey,
        student=request.user
        ).exists():
        messages.info(
        request,
        "You have already completed this survey."
        )
        return redirect("student_survey_list")

    questions = survey.questions.all().order_by("order")

    if request.method == "POST":
        response = SurveyResponse.objects.create(
        survey=survey,
        student=request.user
        )

        for question in questions:
            answer_value = request.POST.get(
            f"question_{question.id}"
            )
            SurveyAnswer.objects.create(
            response=response,
            question=question,
            answer=answer_value
            )
        teacher = survey.teacher
        if teacher.email:
            send_mail(
                    subject=f"new Survey Response: {survey.title}",
                    message=(
                        f"{request.user.get_full_name() or request.user.username} "
                        f"has completed the survey '{survey.title}'."
                        f"\n\nPlease log in to the PandaSpeak platform to review the responses."
                        f"Best regards,"
                        f"\nPandaSpeak Support Team"
                    ),
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[teacher.email],
                    fail_silently=False,
                )

        messages.success(
            request,
            "Thank you. Your survey has been submitted successfully."
            )

        return redirect("student_survey_list")

    return render(
        request,
        "student/take_learning_survey.html",
        {
        "survey": survey,
        "questions": questions,
        }
        )




@login_required(login_url='my_login')
def student_survey_list(request):
    available_surveys = LearningSurvey.objects.filter(
        is_active=True
    ).exclude(
        responses__student=request.user
    )
    return render(
        request,
        'student/student_survey_list.html',
        {
            'available_surveys': available_surveys
        }
    )