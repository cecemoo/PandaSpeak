from django import forms
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core import signing
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_http_methods
from .models import Announcement, AnnouncementDelivery, CustomUser


class PreferenceForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['news_emails']


class AnnouncementForm(forms.ModelForm):
    class Meta:
        model = Announcement
        fields = ['subject', 'body']

    def clean_subject(self):
        value = self.cleaned_data['subject']
        if '\n' in value or '\r' in value:
            raise forms.ValidationError('Use a single line for the subject.')
        return value


def manager(user):
    return user.is_authenticated and user.is_active and (user.is_staff or user.is_superuser)


@login_required(login_url='my_login')
@require_http_methods(['GET', 'POST'])
def preferences(request):
    dashboard = 'manager_dashboard' if manager(request.user) else ('teacher_dashboard' if request.user.is_teacher else 'student_dashboard')
    form = PreferenceForm(request.POST if request.method == 'POST' else None, instance=request.user)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'You have opted in to PandaSpeak news and update emails.' if request.user.news_emails else 'You have opted out of PandaSpeak news and update emails.')
        return redirect(dashboard)
    return render(request, 'account/email_preferences.html', {'opted_in': request.user.news_emails, 'dashboard': dashboard, 'form': form})


@require_http_methods(['GET', 'POST'])
def unsubscribe(request, token):
    try:
        uid = signing.loads(token, salt='pandaspeak-news')
    except signing.BadSignature:
        return render(request, 'account/news_form.html', {'title': 'Invalid unsubscribe link. Please sign in to Email Preferences.'}, status=400)
    user = get_object_or_404(CustomUser, pk=uid)
    if request.method == 'POST':
        CustomUser.objects.filter(pk=user.pk).update(news_emails=False)
        return render(request, 'account/news_form.html', {'title': 'You have unsubscribed from news and update emails.'})
    return render(request, 'account/news_form.html', {'title': 'Unsubscribe from news and updates?', 'button': 'Confirm unsubscribe'})


@user_passes_test(manager, login_url='my_login')
@require_http_methods(['GET', 'POST'])
def compose(request):
    form = AnnouncementForm(request.POST if request.method == 'POST' else None)
    if request.method == 'POST' and form.is_valid():
        announcement = form.save(commit=False)
        announcement.created_by = request.user
        announcement.save()
        return redirect('announcement_preview', pk=announcement.pk)
    return render(request, 'account/news_form.html', {'form': form, 'title': 'News & Update Emails', 'button': 'Save draft and preview', 'history': Announcement.objects.order_by('-created_at')[:5]})


@user_passes_test(manager, login_url='my_login')
@require_http_methods(['GET', 'POST'])
def preview(request, pk):
    announcement = get_object_or_404(Announcement, pk=pk)
    recipients = CustomUser.objects.filter(is_active=True, news_emails=True).exclude(email='')
    if request.method == 'POST' and request.POST.get('confirm') == 'yes':
        with transaction.atomic():
            announcement = Announcement.objects.select_for_update().get(pk=pk)
            if announcement.queued_at is None:
                AnnouncementDelivery.objects.bulk_create([AnnouncementDelivery(announcement=announcement, user_id=uid) for uid in recipients.values_list('pk', flat=True)])
                announcement.queued_at = timezone.now()
                announcement.save(update_fields=['queued_at'])
        return redirect('announcement_preview', pk=pk)
    counts = {status: announcement.deliveries.filter(status=status).count() for status in ['pending', 'sending', 'sent', 'failed', 'skipped']}
    return render(request, 'account/news_preview.html', {'announcement': announcement, 'recipient_count': recipients.count(), 'counts': counts})
