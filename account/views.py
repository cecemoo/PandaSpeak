from django.shortcuts import redirect, render, get_object_or_404
from . forms import CreateUserForm, AddVocabCategoryForm, AddSentenceCategoryForm, AddIdiomCategoryForm, PlacementQuestionForm
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import HttpResponse
from teacher.models import Vocabulary, Sentence, Pronunciation, Idiom, VocabularyCategory, SentenceCategory, IdiomCategory, Tone
from course.models import Course, TimeSlot, Booking
from .models import TermsOfService, PrivacyPolicy, PlacementQuestion, Notification
from datetime import date
from course.forms import CourseForm
from teacher.forms import VocabularyForm, SentenceForm, IdiomForm, PronunciationForm, ToneForm
from django.utils import timezone
from django.contrib import messages
import stripe
from django.conf import settings
from decimal import Decimal, ROUND_HALF_UP
from django.core.mail import send_mail
from student.models import LanguageTest, StudentTestSubmission
from teacher.models import SurveyResponse
from django.urls import resolve





def admin_only(user):
    return user.is_authenticated and (user.is_staff or user.is_superuser)


def home(request):
    vocabulary = Vocabulary.objects.all().order_by('-created_at')
    today_vocabulary = None
    count = vocabulary.count()
    if count > 0:
        index = date.today().toordinal() % count
        today_vocabulary = vocabulary[index]

    sentence = Sentence.objects.all().order_by('-created_at')
    today_sentence = None
    count = sentence.count()
    if count > 0:
        index = date.today().toordinal() % count
        today_sentence = sentence[index]

    idiom = Idiom.objects.all().order_by('-created_at')
    today_idiom = None
    count = idiom.count()
    if count > 0:
        index = date.today().toordinal() % count
        today_idiom = idiom[index]

    tutoring_classes = Course.objects.all().order_by('-created_at')[:3]

    pronunciation = Pronunciation.objects.all().order_by('-created_at')
    today_pronunciation = None
    count = pronunciation.count()
    if count > 0:
        index = date.today().toordinal() % count
        today_pronunciation = pronunciation[index]


    context = {
        'today_vocabulary': today_vocabulary,
        'today_sentence': today_sentence,
        'pronunciation': pronunciation,
        'today_pronunciation': today_pronunciation,
        'today_idiom': today_idiom,
        'tutoring_classes': tutoring_classes,
    }
    return render(request, 'account/index.html', context)


def register(request):
    form = CreateUserForm()
    if request.user.is_authenticated:
        if request.user.is_staff:
            return redirect('manager_dashboard')
        elif request.user.is_teacher:
            return redirect('teacher_dashboard')
        else:
            return redirect('student_dashboard')
    if request.method == 'POST':
        form  = CreateUserForm(request.POST)
        if form.is_valid():
            new_user = form.save()
            user_type = "Teacher" if new_user.is_teacher else "Student"
            send_mail(
                subject="New PandaSpeak Account Registration",
                message=(
                    f"A new account has been registered on PandaSpeak.\n\n"
                    f"Name: {new_user.first_name} {new_user.last_name}\n"
                    f"Email: {new_user.email}\n"
                    f"Account Type: {user_type}\n"
                ),
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=["pandaspeaksupport@gmail.com"],
                fail_silently=False,
            )
            return redirect('my_login')
    context = {'RegisterForm': form}
    return render(request, 'account/register.html', context)


def my_login(request):
    form = AuthenticationForm()
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = request.POST.get('username')
            password = request.POST.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                if user.is_staff or user.is_superuser:
                    return redirect('manager_dashboard')
                elif user.is_teacher:
                    return redirect('teacher_dashboard')
                else: 
                    return redirect('student_dashboard')
    context = {'LoginForm': form}
    return render(request, 'account/my_login.html', context)


def user_logout(request):
    logout(request)
    return redirect('home')



def faq(request):
    return render(request, 'account/faq.html')



def terms(request):
    content = TermsOfService.objects.first()
    context = {'content': content}
    return render(request, 'account/terms.html', context)



def privacy(request):
    content = PrivacyPolicy.objects.first()
    context = {'content': content}
    return render(request, 'account/privacy.html', context)


@login_required(login_url='my_login')
@user_passes_test(admin_only, login_url='my_login')
def manager_dashboard(request):
    vocabulary_category_count = VocabularyCategory.objects.all().count()
    sentence_category_count = SentenceCategory.objects.all().count()
    idiom_category_count = IdiomCategory.objects.all().count()
    course_count = Course.objects.all().count()
    vocabulary_count = Vocabulary.objects.all().count()
    sentence_count = Sentence.objects.all().count()
    idiom_count = Idiom.objects.all().count()
    pronunciation_count = Pronunciation.objects.all().count()
    tone_count = Tone.objects.all().count()

    context = {
        'vocabulary_category_count': vocabulary_category_count,
        'sentence_category_count': sentence_category_count,
        'idiom_category_count': idiom_category_count,
        'course_count': course_count,
        'vocabulary_count': vocabulary_count,
        'sentence_count': sentence_count,
        'idiom_count': idiom_count,
        'pronunciation_count': pronunciation_count,
        'tone_count': tone_count,
    }
    return render(request, 'account/manager_dashboard.html', context)


@login_required(login_url='my_login')
@user_passes_test(admin_only, login_url='my_login')
def categories(request):
    vocabulary_categories = VocabularyCategory.objects.all()
    sentence_categories = SentenceCategory.objects.all()
    idiom_categories = IdiomCategory.objects.all()
    context = {
        'vocabulary_categories': vocabulary_categories,
        'sentence_categories': sentence_categories,
        'idiom_categories': idiom_categories,
    }
    return render(request, 'account/categories.html', context)
    

@login_required(login_url='my_login')
@user_passes_test(admin_only, login_url='my_login')
def add_vocab_category(request):
    if request.method == 'POST':
        form = AddVocabCategoryForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('categories')
    form = AddVocabCategoryForm()
    context = {'AddVocabCategoryForm': form}
    return render(request, 'account/add_vocab_category.html', context)



@login_required(login_url='my_login')
@user_passes_test(admin_only, login_url='my_login')
def add_sentence_category(request):
    if request.method == 'POST':
        form = AddSentenceCategoryForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('categories')
    form = AddSentenceCategoryForm()
    context = {'AddSentenceCategoryForm': form}
    return render(request, 'account/add_sentence_category.html', context)


@login_required(login_url='my_login')
@user_passes_test(admin_only, login_url='my_login')
def add_idiom_category(request):
    if request.method == 'POST':
        form = AddIdiomCategoryForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('categories')
    form = AddIdiomCategoryForm()
    context = {'AddIdiomCategoryForm': form}
    return render(request, 'account/add_idiom_category.html', context)


@login_required(login_url='my_login')
@user_passes_test(admin_only, login_url='my_login')
def edit_vocab_category(request, category_id):
    vocab_category = get_object_or_404(VocabularyCategory, id=category_id)
    if request.method == 'POST':
        form = AddVocabCategoryForm(request.POST, request.FILES, instance=vocab_category)
        if form.is_valid():
            form.save()
            return redirect('categories')
    form = AddVocabCategoryForm(instance=vocab_category)
    context = {'form': form, 'vocab_category': vocab_category}
    return render(request, 'account/edit_vocab_category.html', context)


@login_required(login_url='my_login')
@user_passes_test(admin_only, login_url='my_login')
def edit_sentence_category(request, category_id):
    sentence_category = get_object_or_404(SentenceCategory, id=category_id)
    if request.method == 'POST':
        form = AddSentenceCategoryForm(request.POST, request.FILES, instance=sentence_category)
        if form.is_valid():
            form.save()
            return redirect('categories')
    form = AddSentenceCategoryForm(instance=sentence_category)
    context = {'form': form, 'sentence_category': sentence_category}
    return render(request, 'account/edit_sentence_category.html', context)


@login_required(login_url='my_login')
@user_passes_test(admin_only, login_url='my_login')
def edit_idiom_category(request, category_id):
    idiom_category = get_object_or_404(IdiomCategory, id=category_id)
    if request.method == 'POST':
        form = AddIdiomCategoryForm(request.POST, request.FILES, instance=idiom_category)
        if form.is_valid():
            form.save()
            return redirect('categories')
    form = AddIdiomCategoryForm(instance=idiom_category)
    context = {'form': form, 'idiom_category': idiom_category}
    return render(request, 'account/edit_idiom_category.html', context)


@login_required(login_url='my_login')
@user_passes_test(admin_only, login_url='my_login')
def delete_vocab_category(request, category_id):
    vocab_category = get_object_or_404(VocabularyCategory, id=category_id)
    vocab_category.delete()
    return redirect('categories')


@login_required(login_url='my_login')
@user_passes_test(admin_only, login_url='my_login')
def delete_sentence_category(request, category_id):
    sentence_category = get_object_or_404(SentenceCategory, id=category_id)
    sentence_category.delete()
    return redirect('categories')


@login_required(login_url='my_login')
@user_passes_test(admin_only, login_url='my_login')
def delete_idiom_category(request, category_id):
    idiom_category = get_object_or_404(IdiomCategory, id=category_id)
    idiom_category.delete()
    return redirect('categories')


@login_required(login_url='my_login')
@user_passes_test(admin_only, login_url='my_login')
def vocabularies(request):
    vocabularies = Vocabulary.objects.all().order_by(
        'category__category_name',
        'word'
    )
    context = {'vocabularies': vocabularies}
    return render(request, 'account/vocabularies.html', context)


@login_required(login_url='my_login')
@user_passes_test(admin_only, login_url='my_login')
def edit_vocabulary(request, vocab_id):
    vocab = get_object_or_404(Vocabulary, id=vocab_id)
    if request.method == 'POST':
        form = VocabularyForm(request.POST, request.FILES, instance=vocab)
        if form.is_valid():
            form.save()
            return redirect('vocabularies')
    else:
        form = VocabularyForm(instance=vocab)
    context = {'form': form, 'vocab': vocab}
    return render(request, 'account/edit_vocabulary.html', context)
     # Debugging line to print form errors


@login_required(login_url='my_login')
@user_passes_test(admin_only, login_url='my_login')
def delete_vocabulary(request, vocab_id):
    vocab = get_object_or_404(Vocabulary, id=vocab_id)
    vocab.delete()
    return redirect('vocabularies')


@login_required(login_url='my_login')
@user_passes_test(admin_only, login_url='my_login')
def sentences(request):
    sentences = Sentence.objects.all().order_by(
        'category__category_name',
        'text',
    )
    context = {'sentences': sentences}
    return render(request, 'account/sentences.html', context)


@login_required(login_url='my_login')
@user_passes_test(admin_only, login_url='my_login')
def edit_sentence(request, sentence_id):
    sentence = get_object_or_404(Sentence, id=sentence_id)
    if request.method == 'POST':
        form = SentenceForm(request.POST, request.FILES, instance=sentence)
        if form.is_valid():
            form.save()
            return redirect('sentences')
    form = SentenceForm(instance=sentence)
    context = {'form': form, 'sentence': sentence}
    return render(request, 'account/edit_sentence.html', context)


@login_required(login_url='my_login')
@user_passes_test(admin_only, login_url='my_login')
def delete_sentence(request, sentence_id):
    sentence = get_object_or_404(Sentence, id=sentence_id)
    sentence.delete()
    return redirect('sentences')


@login_required(login_url='my_login')
@user_passes_test(admin_only, login_url='my_login')
def idioms(request):
    idioms = Idiom.objects.all()
    context = {'idioms': idioms}
    return render(request, 'account/idioms.html', context)


@login_required(login_url='my_login')
@user_passes_test(admin_only, login_url='my_login')
def edit_idiom(request, idiom_id):
    idiom = get_object_or_404(Idiom, id=idiom_id)
    if request.method == 'POST':
        form = IdiomForm(request.POST, request.FILES, instance=idiom)
        if form.is_valid():
            form.save()
            return redirect('idioms')
    form = IdiomForm(instance=idiom)
    context = {'form': form, 'idiom': idiom}
    return render(request, 'account/edit_idiom.html', context)


@login_required(login_url='my_login')
@user_passes_test(admin_only, login_url='my_login')
def delete_idiom(request, idiom_id):
    idiom = get_object_or_404(Idiom, id=idiom_id)
    idiom.delete()
    return redirect('idioms')


@login_required(login_url='my_login')
@user_passes_test(admin_only, login_url='my_login')
def pronunciations(request):
    pronunciations = Pronunciation.objects.all()
    context = {'pronunciations': pronunciations}
    return render(request, 'account/pronunciations.html', context)


@login_required(login_url='my_login')
@user_passes_test(admin_only, login_url='my_login')
def edit_pronunciation(request, pronunciation_id):
    pronunciation = get_object_or_404(Pronunciation, id=pronunciation_id)
    if request.method == 'POST':
        form = PronunciationForm(request.POST, request.FILES, instance=pronunciation)
        if form.is_valid():
            form.save()
            return redirect('pronunciations')
    form = PronunciationForm(instance=pronunciation)
    context = {'form': form, 'pronunciation': pronunciation}
    return render(request, 'account/edit_pronunciation.html', context)


@login_required(login_url='my_login')
@user_passes_test(admin_only, login_url='my_login')
def delete_pronunciation(request, pronunciation_id):
    pronunciation = get_object_or_404(Pronunciation, id=pronunciation_id)
    pronunciation.delete()
    return redirect('pronunciations')


@login_required(login_url='my_login')
@user_passes_test(admin_only, login_url='my_login')
def tones(request):
    tones = Tone.objects.all()
    context = {'tones': tones}
    return render(request, 'account/tones.html', context)


@login_required(login_url='my_login')
@user_passes_test(admin_only, login_url='my_login')
def edit_tone(request, tone_id):
    tone = get_object_or_404(Tone, id=tone_id)
    if request.method == 'POST':
        form = ToneForm(request.POST, request.FILES, instance=tone)
        if form.is_valid():
            form.save()
            return redirect('tones')
    form = ToneForm(instance=tone)
    context = {'form': form, 'tone': tone}
    return render(request, 'account/edit_tone.html', context)


@login_required(login_url='my_login')
@user_passes_test(admin_only, login_url='my_login')
def delete_tone(request, tone_id):
    tone = get_object_or_404(Tone, id=tone_id)
    tone.delete()
    return redirect('tones')



@login_required(login_url='my_login')
@user_passes_test(admin_only, login_url='my_login')
def lessons(request):
    courses = Course.objects.all().order_by(
        'teacher__first_name',
        'teacher__last_name',
        'title',
    )
    context = {'courses': courses}
    return render(request, 'account/lessons.html', context)



@login_required(login_url='my_login')
@user_passes_test(admin_only, login_url='my_login')
def delete_lesson(request, lesson_id):
    lesson = get_object_or_404(Course, id=lesson_id)
    lesson.delete()
    return redirect('lessons')



@login_required(login_url='my_login')
@user_passes_test(admin_only, login_url='my_login')
def booking_management(request):
    bookings = Booking.objects.select_related(
        "student", "timeslot", "timeslot__course",
    ).order_by("-created_at")
    return render(request, "account/booking_management.html", {"bookings": bookings})



@login_required(login_url='my_login')
@user_passes_test(admin_only, login_url='my_login')
def refund_booking(request, booking_id):
    booking = get_object_or_404(
        Booking.objects.select_related("timeslot__course"),
        pk=booking_id,
    )
    if booking.status == "refunded" or booking.is_refunded:
        messages.warning(
            request,
            "This booking has already been refunded.",
        )
        return redirect("booking_management")
    if not booking.stripe_payment_intent_id:
        messages.error(
            request,
            "This booking does not have a Stripe payment ID.",
        )
        return redirect("booking_management")
    if not booking.stripe_transfer_id:
        messages.error(
            request,
            "This booking does not have a Stripe teacher transfer ID.",
        )
        return redirect("booking_management")
    # Full price of this individual booking.
    refund_amount = Decimal(str(booking.timeslot.course.price))
    # Convert dollars to Stripe cents.
    refund_amount_cents = int(
        (refund_amount * Decimal("100")).quantize(
            Decimal("1"),
            rounding=ROUND_HALF_UP,
        )
    )
    # Teacher received 80% and PandaSpeak retained 20%.
    teacher_amount = (
        refund_amount * Decimal("0.80")
    ).quantize(
        Decimal("0.01"),
        rounding=ROUND_HALF_UP,
    )
    teacher_amount_cents = int(
        (teacher_amount * Decimal("100")).quantize(
            Decimal("1"),
            rounding=ROUND_HALF_UP,
        )
    )
    try:
        stripe.api_key = settings.STRIPE_SECRET_KEY
        # 1. Refund only this booking's full price to the student.
        refund = stripe.Refund.create(
            payment_intent=booking.stripe_payment_intent_id,
            amount=refund_amount_cents,
            reason="requested_by_customer",
            metadata={
                "booking_id": str(booking.id),
                "timeslot_id": str(booking.timeslot_id),
                "reason": "manager_refund",
            },
            idempotency_key=f"manager-refund-{booking.id}",
        )
        if refund.status not in ("succeeded", "pending"):
            messages.error(
                request,
                f"Stripe did not complete the refund. "
                f"Refund status: {refund.status}",
            )
            return redirect("booking_management")
        # 2. Reverse only this booking's 80% teacher portion.
        reversal = stripe.Transfer.create_reversal(
            booking.stripe_transfer_id,
            amount=teacher_amount_cents,
            metadata={
                "booking_id": str(booking.id),
                "refund_id": refund.id,
                "reason": "manager_refund",
            },
            idempotency_key=(
                f"manager-transfer-reversal-{booking.id}"
            ),
        )
        # 3. Update PandaSpeak only after both Stripe operations succeed.
        booking.status = "refunded"
        booking.is_refunded = True
        booking.save(
            update_fields=[
                "status",
                "is_refunded",
            ]
        )
        messages.success(
            request,
            (
                f"Booking #{booking.id} was refunded successfully. "
                f"Student refund: ${refund_amount:.2f}. "
                f"Teacher transfer reversed: ${teacher_amount:.2f}. "
                f"Refund ID: {refund.id}. "
                f"Reversal ID: {reversal.id}."
            ),
        )
    except stripe.error.StripeError as error:
        error_message = (
            getattr(error, "user_message", None)
            or str(error)
        )
        messages.error(
            request,
            f"Stripe refund failed: {error_message}",
        )
    except Exception as error:
        messages.error(
            request,
            f"Refund failed: {error}",
        )
    return redirect("booking_management")
    


@login_required(login_url='my_login')
@user_passes_test(admin_only, login_url='my_login')
def add_placement_question(request):
    if request.method == 'POST':
        form = PlacementQuestionForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('manage_placement_questions')
    else:
        form = PlacementQuestionForm()
    return render(request, 'account/add_placement_question.html', {'form': form})


@login_required(login_url='my_login')
@user_passes_test(admin_only, login_url='my_login')
def manage_placement_questions(request):
    questions = PlacementQuestion.objects.all().order_by('level','order')
    return render(
        request,
        'account/manage_placement_questions.html',
        {'questions': questions}
    )


def placement_test(request):
    questions = PlacementQuestion.objects.all().order_by('level', 'order')
    if request.method == 'POST':
        level_scores = {
            'level1': {'correct': 0, 'total': 0},
            'level2': {'correct': 0, 'total': 0},
            'level3': {'correct': 0, 'total': 0},
        }
        for question in questions:
            level_scores[question.level]['total'] += 1

            student_answer = request.POST.get(f'question_{question.id}')
            if student_answer == question.correct_answer:
                level_scores[question.level]['correct'] += 1

        percentages = {}
        for level, score in level_scores.items():
            if score['total'] > 0:
                percentages[level] = (
                    score['correct'] / score['total']

                ) * 100
            else:
                percentages[level] = 0
        if percentages['level1'] < 70:
            recommended_level = 'level I - Beginner'
            recommendation = (
                'We recommend starting with Level I materials '
                'to build a strong foundation in Chinese.'
            )
        elif percentages['level2'] < 70:
            recommended_level = 'Level II - intermediate'
            recommendation = (
                'You have a good foundation in Chinese. '
                'Level II materials are recommended to continue developing your skills.'
            )
        elif percentages['level3'] < 60:
            recommended_level = 'Level II - Intermediate'
            recommendation = (
                'You have a good foundation in Chinese. '
                'Level II materials are recommended to continue developing your skills.'
            )
        else:
            recommended_level = 'Level III - Advanced'
            recommendation = (
                'You demonstrate strong foundational Chinese skills. '
                'Level III materials are recommended for more advanced practice.'
            )

        total_correct = sum(
            score['correct'] for score in level_scores.values()
        )
        total_questions = sum(
            score['total'] for score in level_scores.values()
        )
        if total_questions > 0:
            overall_percentage = round(
                (total_correct / total_questions) * 100
            )
        else:
            overall_percentage = 0

        return render(
            request,
            'account/placement_test_result.html',
            {
                'recommended_level': recommended_level,
                'total_correct': total_correct,
                'total_questions': total_questions,
                'overall_percentage': overall_percentage,
                'recommendation': recommendation,
            }
        )
    return render(
        request,
        'account/placement_test.html',
        {'questions': questions}
    )



@login_required(login_url='my_login')
def notifications(request):
    user_notifications = Notification.objects.filter(
        user=request.user
    ).order_by('-created_at')[:5]

    for notification in user_notifications:
        notification.is_completed = False
        # test notification
        if (
            notification.title == "New Test Available"
            and notification.link
            and '/student/tests/' in notification.link
        ):

            try:
                test_id = notification.link.rstrip('/').split('/')[-1]
                completed_test = StudentTestSubmission.objects.filter(
                    student=request.user,
                    test_id=test_id,
                ).exists()
                if completed_test:
                    notification.is_completed = True
                    if not notification.is_read:
                        notification.is_read = True
                        notification.save(update_fields=['is_read'])
            except (ValueError, IndexError):
                pass
                # survey notification
        elif notification.link and '/surveys/' in notification.link:
            try:
                match = resolve(notification.link)
                if match.url_name == 'take_learning_survey':
                    survey_id = match.kwargs.get('survey_id')
                    completed_survey = SurveyResponse.objects.filter(
                        student=request.user,
                        survey_id=survey_id,
                    ).exists()
                    if completed_survey:
                        notification.is_completed = True
                        if not notification.is_read:
                            notification.is_read = True
                            notification.save(update_fields=['is_read'])
            except Exception:
                pass
        
    return render(
        request,
        'account/notifications.html',
        {'notifications': user_notifications}
    )


@login_required(login_url='my_login')
def mark_notification_read(request, notification_id):
    notification = get_object_or_404(
        Notification,
        id=notification_id,
        user=request.user
    )
    notification.is_read = True
    notification.save()
    if notification.link:
        return redirect(notification.link)
    return redirect('notifications')