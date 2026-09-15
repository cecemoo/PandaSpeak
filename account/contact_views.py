from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404, redirect, render

from .forms import ContactForm


def contact(request):
    User = get_user_model()
    instructor = None
    instructor_id = request.GET.get('instructor') or request.POST.get('instructor')
    course_id = request.GET.get('course') or request.POST.get('course')
    if instructor_id:
        instructor = get_object_or_404(User, pk=instructor_id, is_teacher=True)

    initial = {}
    if request.user.is_authenticated:
        initial['name'] = request.user.get_full_name()
        initial['email'] = request.user.email
    if instructor:
        initial['subject'] = f"Course inquiry for {instructor.get_full_name() or instructor.email}"

    form = ContactForm(request.POST or None, initial=initial if request.method != 'POST' else None)
    if request.method == 'POST' and form.is_valid():
        recipient = instructor.email if instructor and instructor.email else settings.DEFAULT_FROM_EMAIL

        if request.user.is_authenticated:
            registration_status = 'Registered'
            if request.user.is_staff or request.user.is_superuser:
                role = 'Manager'
            elif request.user.is_teacher:
                role = 'Teacher'
            else:
                role = 'Student'

            try:
                subscription = request.user.subscription
                if subscription.is_active and not subscription.is_cancelled:
                    subscription_status = 'Active'
                elif subscription.is_cancelled:
                    subscription_status = 'Cancelled'
                else:
                    subscription_status = 'Not subscribed'
            except Exception:
                subscription_status = 'Not subscribed'
        else:
            registration_status = 'Not registered / not signed in'
            role = 'Guest'
            subscription_status = 'Not subscribed'

        course_line = f"Course ID: {course_id}\n" if course_id else ''
        contact_message = (
            f"From: {form.cleaned_data['name']} <{form.cleaned_data['email']}>\n"
            f"Registration status: {registration_status}\n"
            f"Role: {role}\n"
            f"Subscription status: {subscription_status}\n"
            f"{course_line}\n"
            f"{form.cleaned_data['message']}"
        )

        send_mail(
            subject=f"PandaSpeak Contact: {form.cleaned_data['subject']}",
            message=contact_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[recipient],
            fail_silently=False,
        )
        if instructor and recipient != settings.DEFAULT_FROM_EMAIL:
            send_mail(
                subject=f"Copy - PandaSpeak Contact: {form.cleaned_data['subject']}",
                message=f"A message was sent to instructor {recipient} from {form.cleaned_data['email']}.\n\n{contact_message}",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[settings.DEFAULT_FROM_EMAIL],
                fail_silently=True,
            )
        request.session['contact_message_sent'] = True
        return redirect('contact')

    sent = request.session.pop('contact_message_sent', False)
    return render(
        request,
        'account/contact.html',
        {'form': form, 'instructor': instructor, 'course_id': course_id, 'sent': sent},
    )
