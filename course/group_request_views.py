from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.http import require_POST

from account.models import Notification
from .forms import CourseForm
from .models import Course, GroupClassRequest
from .views import CourseCreateView


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
            Notification.objects.create(
                user=course.teacher, title='New Group Class Request',
                message=f'{request.user.get_full_name() or request.user.email} requested a group class: {topic}.',
                link=review_url,
            )
            if course.teacher.email:
                send_mail(
                    'PandaSpeak - New Group Class Request',
                    f'A student requested a group class.\n\nTopic: {topic}\nLevel: {group_request.get_level_display()}\nPreferred time: {preferred_times}\nDesired group size: {desired_group_size}\n\nPlease sign in to PandaSpeak to accept or decline the request.',
                    settings.DEFAULT_FROM_EMAIL, [course.teacher.email], fail_silently=True,
                )
            messages.success(request, "Your group class request was sent to the teacher.")
            return redirect('course:my_group_requests')

    return render(request, 'course/request_group_class.html', {'course': course})


@login_required
def my_group_requests(request):
    requests = GroupClassRequest.objects.filter(student=request.user).select_related('teacher', 'source_course', 'created_course')
    return render(request, 'course/my_group_requests.html', {'group_requests': requests})


@login_required
def teacher_group_requests(request):
    requests = GroupClassRequest.objects.filter(teacher=request.user).select_related('student', 'source_course', 'created_course')
    return render(request, 'course/teacher_group_requests.html', {'group_requests': requests})


@login_required
@require_POST
def respond_group_request(request, pk, decision):
    group_request = get_object_or_404(GroupClassRequest, pk=pk, teacher=request.user)
    if group_request.status != 'pending':
        messages.info(request, "This request has already been reviewed.")
        return redirect('course:teacher_group_requests')
    if decision not in ('accepted', 'declined'):
        messages.error(request, "Invalid response.")
        return redirect('course:teacher_group_requests')

    group_request.status = decision
    group_request.save(update_fields=['status', 'updated_at'])
    Notification.objects.create(
        user=group_request.student, title=f'Group Class Request {decision.title()}',
        message=f'Your request for “{group_request.topic}” was {decision} by {request.user.get_full_name() or request.user.email}.',
        link=reverse('course:my_group_requests'),
    )
    if group_request.student.email:
        send_mail(
            f'PandaSpeak - Group Class Request {decision.title()}',
            f'Your group class request for “{group_request.topic}” was {decision}. Please sign in to PandaSpeak for details.',
            settings.DEFAULT_FROM_EMAIL, [group_request.student.email], fail_silently=True,
        )
    messages.success(request, f"Request {decision}.")
    return redirect('course:teacher_group_requests')


class GroupRequestCourseCreateView(CourseCreateView):
    """Create a real group course from an accepted student request."""
    def get_group_request(self):
        return get_object_or_404(
            GroupClassRequest,
            pk=self.kwargs['request_pk'],
            teacher=self.request.user,
            status='accepted',
        )

    def get(self, request, *args, **kwargs):
        group_request = self.get_group_request()
        if group_request.created_course_id:
            messages.info(request, "A group class has already been created from this request.")
            return redirect('course:course_detail', pk=group_request.created_course_id)
        form = CourseForm(initial={
            'title': group_request.topic,
            'description': group_request.message,
            'session_type': 'group',
            'max_students': group_request.desired_group_size,
            'initial_capacity': group_request.desired_group_size,
        })
        return render(request, self.template_name, {'form': form, 'group_request': group_request})

    def post(self, request, *args, **kwargs):
        group_request = self.get_group_request()
        if group_request.created_course_id:
            messages.info(request, "A group class has already been created from this request.")
            return redirect('course:course_detail', pk=group_request.created_course_id)

        form = CourseForm(request.POST, request.FILES)
        if form.is_valid():
            course = form.save(commit=False)
            course.teacher = request.user
            course.session_type = 'group'
            course.save()
            capacity = form.cleaned_data.get('initial_capacity') or course.max_students or group_request.desired_group_size
            self.generate_timeslots_for_course(course=course, capacity=capacity)

            group_request.created_course = course
            group_request.save(update_fields=['created_course', 'updated_at'])

            course_url = reverse('course:course_detail', kwargs={'pk': course.pk})
            Notification.objects.create(
                user=group_request.student,
                title='Requested Group Class Is Available',
                message=f'The group class “{course.title}” has been created. You can now view the schedule and reserve a seat.',
                link=course_url,
            )
            if group_request.student.email:
                send_mail(
                    'PandaSpeak - Your Requested Group Class Is Available',
                    f'The group class “{course.title}” has been created from your request. Sign in to PandaSpeak to view the schedule and reserve a seat.',
                    settings.DEFAULT_FROM_EMAIL,
                    [group_request.student.email],
                    fail_silently=True,
                )
            messages.success(request, "Group class created. The requesting student has been notified and can now reserve a seat.")
            return redirect('course:course_detail', pk=course.pk)

        return render(request, self.template_name, {'form': form, 'group_request': group_request})
