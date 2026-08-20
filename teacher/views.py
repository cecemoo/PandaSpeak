from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Exists, OuterRef
from teacher.decorators import subscription_required
from . forms import UpdateUserForm, VocabularyForm, SentenceForm, IdiomForm, PronunciationForm, ToneForm, LanguageTestForm, TestQuestionForm, LearningSurveyForm, SurveyQuestionForm
from account.models import CustomUser, Notification
from subscription.models import Subscription
from course.models import Course, Booking, StudentGroup
from . decorators import add_teacher_local_times
from django.shortcuts import get_object_or_404
from django.contrib import messages
from student.models import LanguageTest, TestQuestion, StudentTestSubmission
from .models import LearningSurvey, SurveyQuestion
from django.core.mail import send_mail
from django.conf import settings
from course.forms import StudentGroupForm
from django.urls import reverse




@login_required(login_url='my_login')
def teacher_dashboard(request):
    courses = (
        Course.objects
        .filter(teacher=request.user)
        .annotate(
            booking_count=Count(
                "time_slots__bookings",
                distinct=True,
            ),
            timeslot_count=Count(
                "time_slots",
                distinct=True,
            ),
        )
        .order_by("-created_at")
    )
    recent_bookings = (
        Booking.objects
        .filter(
            timeslot__course__teacher=request.user,
        )
        .select_related(
            "student",
            "timeslot",
            "timeslot__course",
        )
        .order_by("-created_at")[:10]
    )
    add_teacher_local_times(recent_bookings)

    student_groups = StudentGroup.objects.filter(
        teacher=request.user,
        is_active=True,
    ).order_by("name")

    context = {
        "courses": courses,
        "recent_bookings": recent_bookings,
        "student_groups": student_groups,
    }
    return render(
        request,
        "teacher/teacher_dashboard.html",
        context,
    )



@login_required(login_url='my_login')
def create_student_group(request):
    if request.method == "POST":
        form = StudentGroupForm(request.POST)
        if form.is_valid():
            student_group = form.save(commit=False)
            student_group.teacher = request.user
            student_group.save()
            form.save_m2m()
            return redirect("teacher_dashboard")
    else:
        form = StudentGroupForm()
    context = {
        "form": form,
    }
    return render(
        request,
        "teacher/create_student_group.html",
        context
    )


@login_required(login_url='my_login')
def student_group_list(request):
    student_groups = (
        StudentGroup.objects
        .filter(teacher=request.user)
        .prefetch_related("students")
        .order_by("name")
    )
    context = {
        "student_groups": student_groups,
    }
    return render(
        request,
        "teacher/student_group_list.html",
        context,
    )


@login_required(login_url='my_login')
def edit_student_group(request, group_id):
    student_group = get_object_or_404(
        StudentGroup,
        id=group_id,
        teacher=request.user,
    )
    if request.method == "POST":
        form = StudentGroupForm(request.POST, instance=student_group)
        if form.is_valid():
            form.save()
            return redirect("student_group_list")
    else:
        form = StudentGroupForm(instance=student_group)
    context = {
        "form": form,
        "student_group": student_group,
    }
    return render(
        request,
        "teacher/edit_student_group.html",
        context
    )

@login_required(login_url='my_login')
def delete_student_group(request, group_id):
    student_group = get_object_or_404(
        StudentGroup,
        id=group_id,
        teacher=request.user,
    )
    if request.method == "POST":
        student_group.delete()
    return redirect("student_group_list")



@login_required(login_url='my_login')
def account_management(request):
    form = UpdateUserForm(instance=request.user)
    if request.method == 'POST':
        form = UpdateUserForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('teacher_dashboard')
    context = {'UpdateUserForm': form}
    return render(request, 'teacher/account_management.html', context)





def add_vocabulary(request):
    if request.method == 'POST':
        form = VocabularyForm(request.POST, request.FILES)
        
        if form.is_valid():
            vocabulary = form.save(commit=False)

            if hasattr(vocabulary, "teacher"):
                vocabulary.teacher = request.user
            vocabulary.save()

            if request.user.is_staff:
                return redirect('vocabularies')
            else:
                return redirect('teacher_dashboard')
    else:
        form = VocabularyForm()
    context = {'form': form}
    return render(request, 'teacher/add_vocabulary.html', context)



def add_sentence(request):
    if request.method == 'POST':
        form = SentenceForm(request.POST, request.FILES)
        if form.is_valid():
            sentence = form.save(commit=False)

            if hasattr(sentence, "teacher"):
                sentence.teacher = request.user
            sentence.save()

            if request.user.is_staff:
                return redirect('sentences')
            else:
                return redirect('teacher_dashboard')
    else:
        form = SentenceForm()
    context = {'form': form}
    return render(request, 'teacher/add_sentence.html', context)





def add_idiom(request):
    if request.method == 'POST':
        form = IdiomForm(request.POST, request.FILES)
        if form.is_valid():
            idiom = form.save(commit=False)

            if hasattr(idiom, "teacher"):
                idiom.teacher = request.user
            idiom.save()

            if request.user.is_staff:
                return redirect('idioms')
            else:
                return redirect('teacher_dashboard')
    else:
        form = IdiomForm()
    return render(request, 'teacher/add_idiom.html', {'form': form})





def add_pronunciation(request):
    if request.method == 'POST':
        form = PronunciationForm(request.POST, request.FILES)
        if form.is_valid():
            pronunciation = form.save(commit=False)

            if hasattr(pronunciation, "teacher"):
                pronunciation.teacher = request.user
            pronunciation.save()

            if request.user.is_staff:
                return redirect('pronunciations')
            else:
                return redirect('teacher_dashboard')
    else:
        form = PronunciationForm()
    return render(request, 'teacher/add_pronunciation.html', {'form': form})




@login_required(login_url='my_login')
def delete_account(request):
    if request.method == 'POST':
        deleteUser = CustomUser.objects.get(email=request.user)
        deleteUser.delete()
        return redirect('home')
    return render(request, 'teacher/delete_account.html')




def add_tone(request):
    if request.method == 'POST':
        form = ToneForm(request.POST, request.FILES)
        if form.is_valid():
            tone = form.save(commit=False)

            if hasattr(tone, "teacher"):
                tone.teacher = request.user
            tone.save()

            if request.user.is_staff:
                return redirect('tones')
            else:
                return redirect('teacher_dashboard')
    else:
        form = ToneForm()
    return render(request, 'teacher/add_tone.html', {'form': form})


@login_required(login_url='my_login')
def teacher_course_bookings(request):
    booking_exists = Booking.objects.filter(
        timeslot__course=OuterRef("pk")
    )
    courses = Course.objects.filter(teacher=request.user).annotate(has_bookings=Exists(booking_exists))
    bookings = Booking.objects.filter(timeslot__course__teacher=request.user).select_related(
        "student",
        "timeslot",
        "timeslot__course",
    ).order_by(
        "-created_at",
        "timeslot__start_time",
    )

    add_teacher_local_times(bookings)
    context = {
        "courses": courses,
        "bookings": bookings,
    }
    return render(request, "teacher/teacher_course_bookings.html", context)


@login_required(login_url='my_login')
def delete_teacher_course(request, course_id):
    course = get_object_or_404(
        Course,
        pk=course_id,
        teacher=request.user,
    )
    confirmed_bookings = Booking.objects.filter(
        timeslot__course=course,
        status__iexact="confirmed",
    )
    if request.method == "POST":
        if confirmed_bookings.exists():
            messages.error(
                request,
                (
                    "This class cannot be deleted because it has "
                    "confirmed student bookings. Cancel or resolve "
                    "the bookings first."
                ),
            )
            return redirect("teacher_course_bookings")
        course_title = course.title
        course.delete()
        messages.success(
            request,
            f'"{course_title}" was deleted successfully.',
        )
        return redirect("teacher_course_bookings")
    context = {
        "course": course,
        "confirmed_booking_count": confirmed_bookings.count(),
    }
    return render(
        request,
        "teacher/confirm_delete_course.html",
        context,
    )




@login_required(login_url='my_login')
def create_test(request):
    if not request.user.is_teacher:
        return redirect('student_dashboard')
    if request.method == 'POST':
        form = LanguageTestForm(request.POST or None, teacher=request.user)
        if form.is_valid():
            test = form.save(commit=False)
            test.teacher = request.user
            test.save()

            messages.success(request, 'Test created successfully.')
            return redirect('teacher_add_test_questions', test_id=test.id)
    else:
        form = LanguageTestForm(teacher=request.user)
    return render(request, 'teacher/create_test.html', {'form': form})



@login_required(login_url='my_login')
def add_test_questions(request, test_id):
    test = get_object_or_404(LanguageTest, id=test_id, teacher=request.user)
    if request.method == 'POST':
        form = TestQuestionForm(request.POST, request.FILES)
        if form.is_valid():
            question = form.save(commit=False)
            question.test = test
            question.correct_answer = request.POST.get('correct_choice') or request.POST.get('correct_answer')
            question.save()

            messages.success(request, 'Question added successfully.')
            return redirect('teacher_add_test_questions', test_id=test.id)
    else:
        form = TestQuestionForm()
    questions = TestQuestion.objects.filter(test=test).order_by('order')
    return render(request, 'teacher/add_test_questions.html', {'form': form, 'test': test, 'questions': questions})




@login_required(login_url='my_login')
def publish_test(request, test_id):
    test = get_object_or_404(LanguageTest, id=test_id, teacher=request.user)
    if request.method == "POST":
        if not test.questions.exists():
            messages.error(request, "Please add at least one question before publishing the test.")
            return redirect('teacher_add_test_questions', test_id=test.id)
        test.is_published = True
        test.save()
        if not test.notification_sent:
            if test.student_group:
                students = test.student_group.students.filter(
                    is_active=True,
                )
            else:
                students = CustomUser.objects.filter(
                    is_teacher=False,
                    is_active=True,
                    is_staff=False,
                )
            for student in students:
                if student.email:
                    send_mail(
                        subject=f"New PandaSpeak Test: {test.title}",
                        
                        message=(
                            f"Hello {student.get_full_name() or student.email},\n\n"
                            f"A new test '{test.title}' has been published by {test.teacher.get_full_name()}.\n\n"
                            f"Please log into PandaSpeak to take the test.\n\n"
                            f"Best regards,\n"
                            f"PandaSpeak Support Team"
                        ),
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        recipient_list=[student.email],
                        fail_silently=False,
                    )
                Notification.objects.create(
                    user=student,
                    title="New Test Available",
                    message=f"{test.title} has been published by {test.teacher.get_full_name()}. Please log in to take the test.",
                    link=reverse('take_test', args=[test.id]),
                )
            test.notification_sent = True
            test.save()


        messages.success(request, "Test published successfully.")
        return redirect('teacher_dashboard')
    return redirect("teacher_add_test_questions", test_id=test.id)



@login_required(login_url='my_login')
def teacher_test_list(request):
    tests = LanguageTest.objects.filter(teacher=request.user)
    context = {
        'tests': tests,
    }
    return render(request, 'teacher/teacher_test_list.html', context)


@login_required(login_url='my_login')
def delete_test(request, test_id):
    test = get_object_or_404(LanguageTest, id=test_id)
    if request.method == "POST":
        test.delete()
        messages.success(request, 'Test deleted successfully.')
        return redirect('teacher_test_list')



@login_required(login_url='my_login')
def teacher_view_test(request, test_id):
    test = get_object_or_404(LanguageTest, id=test_id)
    questions = test.questions.all().order_by('order')
    context = {
        'test': test,
        'questions': questions,
    }
    return render(request, 'teacher/teacher_view_test.html', context)



@login_required(login_url='my_login')
def student_test_results(request):
    results = StudentTestSubmission.objects.filter(
        test__teacher=request.user
    ).select_related(
        "student",
        "test"
    ).order_by('-submitted_at')

    for result in results:
        result.has_speaking = TestQuestion.objects.filter(
            test=result.test,
            question_type__in=['speaking', 'mixed']
        ).exists()
    context = {
        'results': results,
    }
    return render(request, 'teacher/student_test_results.html', context)




@login_required(login_url='my_login')
def create_learning_survey(request):
    if request.method == "POST":
        form = LearningSurveyForm(request.POST)
        if form.is_valid():
            survey = form.save(commit=False)
            survey.teacher = request.user
            survey.save()
            messages.success(
                request,
                "Survey created successfully. Now add your survey questions."
            )
            return redirect("add_survey_question", survey_id=survey.id)
    else:
        form = LearningSurveyForm()
    return render(
        request,
        "teacher/create_learning_survey.html",
        {"form": form}
    )


@login_required(login_url='my_login')
def add_survey_question(request, survey_id):
    survey = get_object_or_404(
        LearningSurvey,
        id=survey_id,
        teacher=request.user
    )
    if request.method == "POST":
        form = SurveyQuestionForm(request.POST)
        if form.is_valid():
            question = form.save(commit=False)
            question.survey = survey
            question.save()
            messages.success(
                request,
                "Survey question added successfully."
            )
            return redirect(
                "add_survey_question",
                survey_id=survey.id
            )
    else:
        form = SurveyQuestionForm()
    questions = survey.questions.all().order_by("order")
    return render(
        request,
        "teacher/add_survey_question.html",
        {
            "form": form,
            "survey": survey,
            "questions": questions
        }
    )


@login_required(login_url='my_login')
def finish_learning_survey(request,survey_id):
    survey = get_object_or_404(
        LearningSurvey,
        id=survey_id,
        teacher=request.user
    )
    if not survey.questions.exists():
        messages.warning(
            request,
            "Please add at least one question before finishing the survey."
        )
        return redirect(
            "add_survey_question",
            survey_id=survey.id
        )
    survey.is_active = True
    survey.save()
    if survey.student_group:
        students = survey.student_group.students.filter(
            is_active=True
        ).exclude(
            email=""
        )
    else:
        students = CustomUser.objects.filter(
            is_teacher=False,
            is_active=True,
            is_staff=False,
        ).exclude(
            email=""
        )
        
    student_emails = list(
        students.values_list("email", flat=True)
    )
    if student_emails:
        for student in students:
            student_name = student.get_full_name() or student.email
            send_mail(
                subject=f"New Learning Survey: {survey.title}",
                message=(
                    f"Hello, {student_name},\n\n"
                    f"A new learning survey has been published:"
                    f"'{survey.title}'.\n\n"
                    f"Please log into PandaSpeak to complete the survey.\n\n"
                    f"Best regards,\n"
                    f"\nPandaSpeak Support Team"
                ),
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[student.email],
                fail_silently=False,
            )
            Notification.objects.create(
                user=student,
                title="New Learning Survey Available",
                message=f"{survey.title} has been published by {survey.teacher.get_full_name()}. Please log in to complete the survey.",
                link=reverse('take_learning_survey', args=[survey.id]),
            )
    messages.success(
        request,
        "Survey published successfully."
    )
    return redirect(
        "teacher_dashboard"
    )   
    


@login_required(login_url='my_login')
def teacher_survey_list(request):
    surveys = LearningSurvey.objects.filter(
        teacher=request.user
    ).order_by("-created_at")
    return render(
        request,
        "teacher/teacher_survey_list.html",
        {"surveys": surveys}
    )


@login_required(login_url='my_login')
def survey_responses(request, survey_id):
    survey = get_object_or_404(
        LearningSurvey,
        id=survey_id,
        teacher=request.user
    )
    responses = survey.responses.select_related(
        "student"
    ).prefetch_related(
        "answers__question"
    ).order_by("-submitted_at")
    return render(
        request,
        "teacher/survey_responses.html",
        {
            "survey": survey,
            "responses": responses
        }
    )