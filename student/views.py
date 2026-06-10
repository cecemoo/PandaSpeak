from multiprocessing import context

from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required
from student.models import Subscription
from subscription.decorators import subscription_required
from teacher.models import Vocabulary, Sentence, Pronunciation, Idiom
from teacher.models import VocabularyCategory, SentenceCategory, IdiomCategory


@login_required(login_url='my_login')
def student_dashboard(request):
    try:
        subDetails = Subscription.objects.get(user=request.user)
        subscription_plan = subDetails.subscription_plan
        context = {
            'SubPlan': subscription_plan,
        }
        return render(request, 'student/student_dashboard.html', context)
    except:
        subscription_plan = None
        context = {
            'SubPlan': subscription_plan,
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
def vocabulary_page(request):
    vocabularies = Vocabulary.objects.all()
    return render(request, 'student/vocabulary_page.html', {'categories': vocabularies})


@login_required(login_url='my_login')
@subscription_required
def pronunciation_page(request):
    pronunciations = Pronunciation.objects.all()
    return render(request, 'student/pronunciation_page.html', {'pronunciations': pronunciations})


@login_required(login_url='my_login')
@subscription_required
def sentence_page(request):
    sentences = Sentence.objects.all()
    return render(request, 'student/sentence_page.html', {'sentences': sentences})
   


@login_required(login_url='my_login')
@subscription_required
def idiom_page(request):
    idioms = Idiom.objects.all()
    return render(request, 'student/idiom_page.html', {'idioms': idioms})
   




@login_required(login_url='my_login')
def subscription_plans(request):
    return render(request, 'student/subscription_plans.html')


@login_required(login_url='my_login')
def account_management(request):
    return render(request, 'student/account_management.html')