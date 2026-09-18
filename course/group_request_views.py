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
from .forms import RequestedGroupCourseForm
from .models import Course, GroupClassRequest
from .views import CourseCreateView


def _email_name(user):
    """Return a friendly name for PandaSpeak email greetings."""
    return user.get_full_name().strip() or user.email or 'PandaSpeak User'


def _requested_schedule_initial(gr):
    """Convert the next occurrence of the student's requested weekday/time to teacher time."""
    try:
        day_name, remainder = (gr.preferred_times or '').strip().split(', ', 1)
        time_text, timezone_text = remainder.rsplit(' (', 1)
        student_tz_name = timezone_text.rstrip(')')
    except ValueError:
        return {}
    if day_name == 'Flexible' or time_text == 'Flexible': return {}
    weekdays = ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday']
    if day_name not in weekdays: return {}
    try:
        student_tz = ZoneInfo(student_tz_name); requested_clock = datetime.strptime(time_text, '%I:%M %p').time()
    except (ZoneInfoNotFoundError, ValueError): return {}
    teacher_tz_name = getattr(gr.source_course, 'teacher_timezone', None) or settings.TIME_ZONE
    try: teacher_tz = ZoneInfo(teacher_tz_name)
    except (ZoneInfoNotFoundError, ValueError):
        teacher_tz_name = settings.TIME_ZONE; teacher_tz = ZoneInfo(settings.TIME_ZONE)
    today = timezone.now().astimezone(student_tz).date()
    days_ahead = (weekdays.index(day_name) - today.weekday()) % 7
    requested_date = today + timedelta(days=days_ahead)
    student_dt = datetime.combine(requested_date, requested_clock, tzinfo=student_tz)
    teacher_dt = student_dt.astimezone(teacher_tz)
    duration = getattr(gr.source_course, 'duration_minutes', None) or 60
    teacher_end = teacher_dt + timedelta(minutes=duration)
    return {'start_date':teacher_dt.date(),'end_date':teacher_dt.date(),'available_days':[str(teacher_dt.weekday())],'daily_start_time':teacher_dt.strftime('%H:%M'),'daily_end_time':teacher_end.strftime('%H:%M'),'teacher_timezone':teacher_tz_name}


def _ensure_time_choices(form, initial):
    for field_name in ('daily_start_time','daily_end_time'):
        value=initial.get(field_name)
        if not value or field_name not in form.fields: continue
        choices=list(form.fields[field_name].choices)
        if value not in {c[0] for c in choices}:
            choices.append((value,value)); choices.sort(key=lambda item:item[0]); form.fields[field_name].choices=choices


@login_required
def request_group_class(request, course_pk):
    course=get_object_or_404(Course,pk=course_pk)
    if request.user.is_teacher or request.user.is_staff:
        messages.error(request,'Only students can request a group class.'); return redirect('course:course_detail',pk=course.pk)
    if request.method=='POST':
        topic=request.POST.get('topic','').strip(); preferred_day=request.POST.get('preferred_day','').strip(); preferred_time=request.POST.get('preferred_time','').strip(); preferred_timezone=request.POST.get('preferred_timezone','').strip(); message=request.POST.get('message','').strip(); level=request.POST.get('level',request.user.learning_level)
        try: desired_group_size=max(2,min(20,int(request.POST.get('desired_group_size',4))))
        except (TypeError,ValueError): desired_group_size=4
        try:
            requested_price=int(request.POST.get('requested_price',''))
            if requested_price < 1: raise ValueError
        except (TypeError,ValueError): requested_price=None
        if not topic or not preferred_day or not preferred_time or not preferred_timezone or requested_price is None:
            messages.error(request,'Please provide a topic, preferred day, time, time zone, and proposed price per student.')
        else:
            preferred_times=f'{preferred_day}, {preferred_time} ({preferred_timezone})'
            gr=GroupClassRequest.objects.create(student=request.user,teacher=course.teacher,source_course=course,topic=topic,level=level,preferred_times=preferred_times,desired_group_size=desired_group_size,requested_price=requested_price,message=message)
            Notification.objects.create(user=course.teacher,title='New Group Class Request',message=f'{request.user.get_full_name() or request.user.email} requested a group class: {topic} at ${requested_price} per student.',link=reverse('course:teacher_group_requests'))
            if course.teacher.email:
                body=(f'Dear {_email_name(course.teacher)},\n\n'
                      f'You have received a new group class request from {_email_name(request.user)}.\n\n'
                      f'Topic: {topic}\nLevel: {gr.get_level_display()}\nPreferred time: {preferred_times}\nDesired group size: {desired_group_size}\nProposed price per student: ${requested_price}\n'
                      f'{("Student message: " + message + chr(10)) if message else ""}\n'
                      'Please sign in to PandaSpeak to review the request and choose whether to accept or decline it. You will be able to review the requested details before creating the class.\n\n'
                      'Thank you for teaching with PandaSpeak.\n\nBest regards,\nPandaSpeak Team')
                send_mail('PandaSpeak - New Group Class Request',body,settings.DEFAULT_FROM_EMAIL,[course.teacher.email],fail_silently=True)
            messages.success(request,'Your group class request was sent to the teacher. The teacher will decide whether to accept the requested class and price.')
            return redirect('course:my_group_requests')
    return render(request,'course/request_group_class.html',{'course':course})


@login_required
def my_group_requests(request):
    qs=GroupClassRequest.objects.filter(student=request.user).select_related('teacher','source_course','created_course'); return render(request,'course/my_group_requests.html',{'group_requests':qs})

@login_required
def teacher_group_requests(request):
    qs=GroupClassRequest.objects.filter(teacher=request.user).select_related('student','source_course','created_course'); return render(request,'course/teacher_group_requests.html',{'group_requests':qs})

@login_required
@require_POST
def respond_group_request(request,pk,decision):
    gr=get_object_or_404(GroupClassRequest,pk=pk,teacher=request.user)
    if gr.status!='pending': messages.info(request,'This request has already been reviewed.'); return redirect('course:teacher_group_requests')
    if decision not in ('accepted','declined'): messages.error(request,'Invalid response.'); return redirect('course:teacher_group_requests')
    gr.status=decision; gr.save(update_fields=['status','updated_at'])
    Notification.objects.create(user=gr.student,title=f'Group Class Request {decision.title()}',message=f'Your request for “{gr.topic}” was {decision} by {request.user.get_full_name() or request.user.email}.',link=reverse('course:my_group_requests'))
    if gr.student.email:
        if decision == 'accepted':
            body=(f'Dear {_email_name(gr.student)},\n\n'
                  f'Good news! Your group class request for “{gr.topic}” has been accepted by {_email_name(request.user)}.\n\n'
                  f'Requested time: {gr.preferred_times}\nDesired group size: {gr.desired_group_size}\nProposed price per student: ${gr.requested_price}\n\n'
                  'The teacher will now finalize the class details. We will notify you again when the group class is available so you can review the final schedule and price before reserving and paying for a seat.\n\n'
                  'Thank you for learning with PandaSpeak.\n\nBest regards,\nPandaSpeak Team')
        else:
            body=(f'Dear {_email_name(gr.student)},\n\n'
                  f'Your group class request for “{gr.topic}” was not accepted at this time.\n\n'
                  'You can sign in to PandaSpeak to review your requests and explore other available tutoring options. You may also submit another group class request when appropriate.\n\n'
                  'Thank you for your interest in learning with PandaSpeak.\n\nBest regards,\nPandaSpeak Team')
        send_mail(f'PandaSpeak - Group Class Request {decision.title()}',body,settings.DEFAULT_FROM_EMAIL,[gr.student.email],fail_silently=True)
    messages.success(request,f'Request {decision}.'); return redirect('course:teacher_group_requests')


class GroupRequestCourseCreateView(CourseCreateView):
    def get_group_request(self): return get_object_or_404(GroupClassRequest,pk=self.kwargs['request_pk'],teacher=self.request.user,status='accepted')
    def get(self,request,*args,**kwargs):
        gr=self.get_group_request()
        if gr.created_course_id: messages.info(request,'A group class has already been created from this request.'); return redirect('course:course_detail',pk=gr.created_course_id)
        schedule=_requested_schedule_initial(gr)
        initial={'title':gr.topic,'max_students':gr.desired_group_size,'initial_capacity':gr.desired_group_size,'price':gr.requested_price,**schedule}
        form=RequestedGroupCourseForm(initial=initial); _ensure_time_choices(form,schedule)
        return render(request,self.template_name,{'form':form,'group_request':gr,'creation_mode':'group','page_title':'Create Group Class from Request','requested_schedule_converted':bool(schedule)})
    def post(self,request,*args,**kwargs):
        gr=self.get_group_request()
        if gr.created_course_id: messages.info(request,'A group class has already been created from this request.'); return redirect('course:course_detail',pk=gr.created_course_id)
        schedule=_requested_schedule_initial(gr); form=RequestedGroupCourseForm(request.POST); _ensure_time_choices(form,schedule)
        if form.is_valid():
            course=form.save(commit=False); course.teacher=request.user; course.session_type='group'; course.description=''; course.save()
            capacity=form.cleaned_data.get('initial_capacity') or course.max_students or gr.desired_group_size
            self.generate_timeslots_for_course(course=course,capacity=capacity)
            gr.created_course=course; gr.status='converted'; gr.save(update_fields=['created_course','status','updated_at'])
            course_url=reverse('course:course_detail',kwargs={'pk':course.pk})
            Notification.objects.create(user=gr.student,title='Requested Group Class Is Available',message=f'The group class “{course.title}” has been created. You can now view the schedule and reserve a seat.',link=course_url)
            if gr.student.email:
                body=(f'Dear {_email_name(gr.student)},\n\n'
                      f'Your requested group class, “{course.title},” is now available on PandaSpeak.\n\n'
                      f'Final price per student: ${course.price}\n'
                      f'Duration: {course.duration_minutes} minutes\n\n'
                      'Please sign in to PandaSpeak to review the final class schedule and details. If everything works for you, you can reserve and pay for your seat.\n\n'
                      'We hope you enjoy your class!\n\nBest regards,\nPandaSpeak Team')
                send_mail('PandaSpeak - Your Requested Group Class Is Available',body,settings.DEFAULT_FROM_EMAIL,[gr.student.email],fail_silently=True)
            messages.success(request,'Group class created. The requesting student has been notified and can now reserve a seat.'); return redirect('course:course_detail',pk=course.pk)
        return render(request,self.template_name,{'form':form,'group_request':gr,'creation_mode':'group','page_title':'Create Group Class from Request','requested_schedule_converted':bool(schedule)})
