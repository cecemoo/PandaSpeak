from django.shortcuts import redirect, render
from . forms import CreateUserForm, AddVocabCategoryForm, AddSentenceCategoryForm, AddIdiomCategoryForm
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import HttpResponse
from teacher.models import Vocabulary, Sentence, Pronunciation, Idiom, VocabularyCategory, SentenceCategory, IdiomCategory, Tone
from course.models import Course, TimeSlot
from .models import TermsOfService, PrivacyPolicy
from datetime import date
from course.forms import CourseForm
from django.shortcuts import get_object_or_404
from teacher.forms import VocabularyForm, SentenceForm, IdiomForm, PronunciationForm, ToneForm
from django.utils import timezone
from course.views import generate_timeslots_for_course




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
            form.save()
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


@login_required(login_url='my_login')
@user_passes_test(admin_only, login_url='my_login')
def faq(request):
    return render(request, 'account/faq.html')


@login_required(login_url='my_login')
@user_passes_test(admin_only, login_url='my_login')
def terms(request):
    content = TermsOfService.objects.first()
    context = {'content': content}
    return render(request, 'account/terms.html', context)


@login_required(login_url='my_login')
@user_passes_test(admin_only, login_url='my_login')
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
    vocabularies = Vocabulary.objects.all()
    context = {'vocabularies': vocabularies}
    return render(request, 'account/vocabularies.html', context)


@login_required(login_url='my_login')
@user_passes_test(admin_only, login_url='my_login')
def edit_vocabulary(request, vocab_id):
    vocab = get_object_or_404(Vocabulary, id=vocab_id)
    if request.method == 'POST':
        print("files:", request.FILES)
        print("post:", request.POST)
        form = VocabularyForm(request.POST, request.FILES, instance=vocab)
        if form.is_valid():
            form.save()
            return redirect('vocabularies')
    form = VocabularyForm(instance=vocab)
    context = {'form': form, 'vocab': vocab}
    return render(request, 'account/edit_vocabulary.html', context)


@login_required(login_url='my_login')
@user_passes_test(admin_only, login_url='my_login')
def delete_vocabulary(request, vocab_id):
    vocab = get_object_or_404(Vocabulary, id=vocab_id)
    vocab.delete()
    return redirect('vocabularies')


@login_required(login_url='my_login')
@user_passes_test(admin_only, login_url='my_login')
def sentences(request):
    sentences = Sentence.objects.all()
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
    courses = Course.objects.all()
    context = {'courses': courses}
    return render(request, 'account/lessons.html', context)



@login_required(login_url='my_login')
@user_passes_test(admin_only, login_url='my_login')
def delete_lesson(request, lesson_id):
    lesson = get_object_or_404(Course, id=lesson_id)
    lesson.delete()
    return redirect('lessons')