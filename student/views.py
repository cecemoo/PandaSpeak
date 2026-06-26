from multiprocessing import context
from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required
from subscription.models import Subscription
from subscription.decorators import subscription_required
from teacher.models import Vocabulary, Sentence, Pronunciation, Idiom, Tone, VocabularyCategory, SentenceCategory, IdiomCategory
from datetime import date


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

    context = {
        'has_subscription': sub is not None,
        'SubPlan': sub.subscription_plan if sub else 'No Active Subscription'
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
        "SubPlan": sub.subscription_plan if sub else 'No Active Subscription'
    }
    return render(request, 'student/account_management.html', context)



@login_required(login_url='my_login')
def subscription_locked(request):
    return render(request, 'student/subscription_locked.html')



