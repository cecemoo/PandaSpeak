from datetime import datetime, timedelta
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.http import require_POST

from account.models import Notification
from .forms import GroupCourseForm
from .models import Course, GroupClassRequest
from .views import CourseCreateView


def _requested_schedule_initial(group_request):
    """Convert a student's requested weekday/time into the teacher's timezone."""
    raw = (group_request.preferred_times or '').strip()
    try:
        day_name, remainder = raw.split(', ', 1)
        time_text, timezone_text = remainder.rsplit(' (', 1)
        student_timezone_name = timezone_text.rstrip(')')
    except ValueError:
        return {}

    if day_name == 'Flexible' or time_text == 'Flexible':
        return {}

    weekday_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    if day_name not in weekday_names:
        return {}

    try:
        student_tz = ZoneInfo(student_timezone_name)
    except (ZoneInfoNotFoundError, ValueError):
        return {}

    teacher_timezone_name = (
        getattr(group_request.source_course, 'teacher_timezone', None)
        or settings.TIME_ZONE
    )
    try:
        teacher_tz = ZoneInfo(teacher_timezone_name)
    except (ZoneInfoNotFoundError, ValueError):
        teacher_timezone_name = settings.TIME_ZONE
        teacher_tz = ZoneInfo(settings.TIME_ZONE)

    try:
        requested_clock = datetime.strptime(time_text, '%I:%M %p').time()
    except ValueError:
        return {}

    student_today = timezone.now().astimezone(student_tz).date()
    requested_weekday = weekday_names.index(day_name)
    days_ahead = (requested_weekday - student_today.weekday()) % 7
    requested_date = student_today + timedelta(days=days_ahead)
    student_dt = datetime.combine(requested_date, requested_clock, tzinfo=student_tz)
    teacher_dt = student_dt.astimezone(teacher_tz)

    duration = 60
    if group_request.source_course and group_request.source_course.duration_minutes:
        duration = group_request.source_course.duration_minutes
    teacher_end = teacher_dt + timedelta(minutes=duration)

    return {
        'start_date': teacher_dt.date(),
        'end_date': teacher_dt.date(),
        'available_days': [str(teacher_dt.weekday())],
        'daily_start_time': teacher_dt.strftime('%H:%M'),
        'daily_end_time': teacher_end.strftime('%H:%M'),
        'teacher_timezone': teacher_timezone_name,
    }


def _ensure_time_choices(form, initial):
    """Allow half-hour or other requested times even when not in the standard hourly choices."""
    for field_name in ('daily_start_time', 'daily_end_time'):
        value = initial.get(field_name)
        if not value or field_name not in form.fields:
            continue
        choices = list(form.fields[field_name].choices)
        if value not in {choice[0] for choice in choices}:
            choices.append((value, value))
            choices.sort(key=lambda item: item[0])
            form.fields[field_name].choices = choices


@login_required
def request_group_class(request, course_pk):
    course = get_object_or_404(Course, pk=course_pk)
    if request.user.is_teacher or request.user.is_staff:
        messages.error(request, "Only students can request a group class.")
        return redirect('course:course_detail', pk=course.pk)

    if request.method == 'POST':
        topic = request.POST.get('topic', '').strip()
        preferred_day = request.POST.get('preferred_day', '').strip()
        preferred_time = request.POST.get('preferred_time', '').strip()
        preferred_timezone = request.POST.get('preferred_timezone', '').strip()
        message = request.POST.get('message', '').strip()
        level = request.POST.get('level', request.user.learning_level)
        try:
            desired_group_size = max(2, min(20, int(request.POST.get('desired_group_size', 4))))
        except (TypeError, ValueError):
            desired_group_size = 4

        if not topic or not preferred_day or not preferred_time or not preferred_timezone:
            messages.error(request, "Please provide a topic, preferred day, time, and time zone.")
        else:
            preferred_times = f'{preferred_day}, {preferred_time} ({preferred_timezone})'
            group_request = GroupClassRequest.objects.create(
                student=request.user, teacher=course.teacher, source_course=course,
                topic=topic, level=level, preferred_times=preferred_times,
                desired_group_size=desired_group_size, message=message,
            )
            review_url = reverse('course:teacher_group_requests')
            Notification.objects.create(user=course.teacher,title='New Group Class Request',message=f'{request.user.get_full_name() or request.user.email} requested a group class: {topic}.',link=review_url)
            if course.teacher.email:
                send_mail('PandaSpeak - New Group Class Request',f'A student requested a group class.\n\nTopic: {topic}\nLevel: {group_request.get_level_display()}\nPreferred time: {preferred_times}\nDesired group size: {desired_group_size}\n\nPlease sign in to PandaSpeak to accept or decline the request.',settings.DEFAULT_FROM_EMAIL,[course.teacher.email],fail_silently=True)
            messages.success(request, "Your group class request was sent to the teacher.")
            return redirect('course:my_group_requests')
    return render(request, 'course/request_group_class.html', {'course': course})


@login_required
def my_group_requests(request):
    requests = GroupClassRequest.objects.filter(student=request.user).select_related('teacher','source_course','created_course')
    return render(request,'course/my_group_requests.html',{'group_requests':requests})


@login_required
def teacher_group_requests(request):
    requests = GroupClassRequest.objects.filter(teacher=request.user).select_related('student','source_course','created_course')
    return render(request,'course/teacher_group_requests.html',{'group_requests':requests})


@login_required
@require_POST
def respond_group_request(request, pk, decision):
    group_request=get_object_or_404(GroupClassRequest,pk=pk,teacher=request.user)
    if group_request.status!='pending':
        messages.info(request,"This request has already been reviewed.")
        return redirect('course:teacher_group_requests')
    if decision not in ('accepted','declined'):
        messages.error(request,"Invalid response.")
        return redirect('course:teacher_group_requests')
    group_request.status=decision
    group_request.save(update_fields=['status','updated_at'])
    Notification.objects.create(user=group_request.student,title=f'Group Class Request {decision.title()}',message=f'Your request for “{group_request.topic}” was {decision} by {request.user.get_full_name() or request.user.email}.',link=reverse('course:my_group_requests'))
    if group_request.student.email:
        send_mail(f'PandaSpeak - Group Class Request {decision.title()}',f'Your group class request for “{group_request.topic}” was {decision}. Please sign in to PandaSpeak for details.',settings.DEFAULT_FROM_EMAIL,[group_request.student.email],fail_silently=True)
    messages.success(request,f"Request {decision}.")
    return redirect('course:teacher_group_requests')


class GroupRequestCourseCreateView(CourseCreateView):
    """Create a group class from an accepted request, prefilled in the teacher's timezone."""
    def get_group_request(self):
        return get_object_or_404(GroupClassRequest,pk=self.kwargs['request_pk'],teacher=self.request.user,status='accepted')

    def get(self,request,*args,**kwargs):
        gr=self.get_group_request()
        if gr.created_course_id:
            messages.info(request,"A group class has already been created from this request.")
            return redirect('course:course_detail',pk=gr.created_course_id)
        schedule_initial = _requested_schedule_initial(gr)
        initial = {
            'title':gr.topic,
            'description':gr.message,
            'max_students':gr.desired_group_size,
            'initial_capacity':gr.desired_group_size,
            **schedule_initial,
        }
        form=GroupCourseForm(initial=initial)
        _ensure_time_choices(form, schedule_initial)
        return render(request,self.template_name,{
            'form':form,
            'group_request':gr,
            'creation_mode':'group',
            'page_title':'Create Group Class from Request',
            'requested_schedule_converted': bool(schedule_initial),
        })

    def post(self,request,*args,**kwargs):
        gr=self.get_group_request()
        if gr.created_course_id:
            messages.info(request,"A group class has already been created from this request.")
            return redirect('course:course_detail',pk=gr.created_course_id)
        form=GroupCourseForm(request.POST,request.FILES)
        schedule_initial = _requested_schedule_initial(gr)
        _ensure_time_choices(form, schedule_initial)
        if form.is_valid():
            course=form.save(commit=False)
            course.teacher=request.user
            course.session_type='group'
            course.save()
            capacity=form.cleaned_data.get('initial_capacity') or course.max_students or gr.desired_group_size
            self.generate_timeslots_for_course(course=course,capacity=capacity)
            gr.created_course=course
            gr.status='converted'
            gr.save(update_fields=['created_course','status','updated_at'])
            course_url=reverse('course:course_detail',kwargs={'pk':course.pk})
            Notification.objects.create(user=gr.student,title='Requested Group Class Is Available',message=f'The group class “{course.title}” has been created. You can now view the schedule and reserve a seat.',link=course_url)
            if gr.student.email:
                send_mail('PandaSpeak - Your Requested Group Class Is Available',f'The group class “{course.title}” has been created from your request. Sign in to PandaSpeak to view the schedule and reserve a seat.',settings.DEFAULT_FROM_EMAIL,[gr.student.email],fail_silently=True)
            messages.success(request,"Group class created. The requesting student has been notified and can now reserve a seat.")
            return redirect('course:course_detail',pk=course.pk)
        return render(request,self.template_name,{
            'form':form,
            'group_request':gr,
            'creation_mode':'group',
            'page_title':'Create Group Class from Request',
            'requested_schedule_converted': bool(schedule_initial),
        })
