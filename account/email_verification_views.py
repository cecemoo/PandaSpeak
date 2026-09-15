from django.conf import settings
from django.contrib import messages
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode

from .forms import CreateUserForm
from .models import CustomUser, Notification
from .push import send_push_to_user


def _send_verification_email(request, user):
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = default_token_generator.make_token(user)
    verification_url = request.build_absolute_uri(
        reverse('verify_email', kwargs={'uidb64': uid, 'token': token})
    )
    send_mail(
        subject='Verify Your PandaSpeak Email',
        message=(
            f'Hello {user.first_name or "PandaSpeak learner"},\n\n'
            'Thank you for registering with PandaSpeak. Please verify your email address by opening the link below:\n\n'
            f'{verification_url}\n\n'
            'After verification, you can sign in to PandaSpeak.\n\n'
            'If you did not create this account, you can ignore this email.'
        ),
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        fail_silently=False,
    )


def register(request):
    if request.user.is_authenticated:
        if request.user.is_staff:
            return redirect('manager_dashboard')
        if request.user.is_teacher:
            return redirect('teacher_dashboard')
        return redirect('student_dashboard')

    form = CreateUserForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        new_user = form.save(commit=False)
        # Only registrations created through this new flow start inactive.
        # Existing users in the database are never modified.
        new_user.is_active = False
        new_user.save()
        _send_verification_email(request, new_user)

        user_type = 'Teacher' if new_user.is_teacher else 'Student'
        managers = CustomUser.objects.filter(is_staff=True, is_active=True)
        registration_message = (
            f'{new_user.get_full_name() or new_user.email} '
            f'registered a new {user_type.lower()} account and is awaiting email verification.'
        )
        for manager in managers:
            Notification.objects.create(
                user=manager,
                title='New Account Registration',
                message=registration_message,
                link=reverse('manager_dashboard'),
            )
            send_push_to_user(
                manager,
                'New Account Registration',
                registration_message,
                reverse('manager_dashboard'),
            )

        return render(request, 'account/verification_sent.html', {'email': new_user.email})

    return render(request, 'account/register.html', {'RegisterForm': form})


def verify_email(request, uidb64, token):
    try:
        user_id = force_str(urlsafe_base64_decode(uidb64))
        user = CustomUser.objects.get(pk=user_id)
    except (TypeError, ValueError, OverflowError, CustomUser.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        if not user.is_active:
            user.is_active = True
            user.save(update_fields=['is_active'])
        messages.success(request, 'Your email has been verified. You can now sign in to PandaSpeak.')
        return redirect('my_login')

    return render(request, 'account/verification_invalid.html', status=400)
