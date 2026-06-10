from django.shortcuts import redirect, render
from . forms import CreateUserForm
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse

def home(request):
    return render(request, 'account/index.html')


def register(request):
    form = CreateUserForm()
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
            if user is not None and user.is_teacher==True:
                login(request, user)
                return redirect('teacher_dashboard')
            if user is not None and user.is_teacher==False:
                login(request, user)
                return redirect('student_dashboard')
    context = {'LoginForm': form}
    return render(request, 'account/my_login.html', context)


def user_logout(request):
    logout(request)
    return redirect('home')