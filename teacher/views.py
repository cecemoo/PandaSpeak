from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required

from teacher.decorators import subscription_required
from . forms import UpdateUserForm, VocabularyForm, SentenceForm, IdiomForm, PronunciationForm, ToneForm
from account.models import CustomUser
from subscription.models import Subscription








@login_required(login_url='my_login')
def teacher_dashboard(request):
    return render(request, 'teacher/teacher_dashboard.html')



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
