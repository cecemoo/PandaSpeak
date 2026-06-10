from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required

from teacher.decorators import subscription_required
from . forms import UpdateUserForm, VocabularyForm, SentenceForm, IdiomForm, PronunciationForm
from account.models import CustomUser
from student.models import Subscription









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




@login_required(login_url='my_login')
def add_vocabulary(request):
    if request.method == 'POST':
        form = VocabularyForm(request.POST, request.FILES)
        if form.is_valid():
            vocabulary = form.save(commit=False)
            vocabulary.teacher = request.user
            vocabulary.save()
            return redirect('teacher_dashboard')
    else:
        form = VocabularyForm()
    return render(request, 'teacher/add_vocabulary.html', {'form': form})


@login_required(login_url='my_login')
def add_sentence(request):
    if request.method == 'POST':
        form = SentenceForm(request.POST, request.FILES)
        if form.is_valid():
            sentence = form.save(commit=False)
            sentence.teacher = request.user
            sentence.save()
            return redirect('teacher_dashboard')
    else:
        form = SentenceForm()
    return render(request, 'teacher/add_sentence.html', {'form': form})




@login_required(login_url='my_login')
def add_idiom(request):
    if request.method == 'POST':
        form = IdiomForm(request.POST, request.FILES)
        if form.is_valid():
            idiom = form.save(commit=False)
            idiom.teacher = request.user
            idiom.save()
            return redirect('teacher_dashboard')
    else:
        form = IdiomForm()
    return render(request, 'teacher/add_idiom.html', {'form': form})




@login_required(login_url='my_login')
def add_pronunciation(request):
    if request.method == 'POST':
        form = PronunciationForm(request.POST, request.FILES)
        if form.is_valid():
            pronunciation = form.save(commit=False)
            pronunciation.teacher = request.user
            pronunciation.save()
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
