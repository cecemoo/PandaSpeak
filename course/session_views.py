import uuid
from datetime import timedelta

from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.http import require_POST

from account.models import Notification
from .models import Booking, SessionAttendance


PRESENCE_TIMEOUT = timedelta(minutes=2)
JOIN_EARLY_WINDOW = timedelta(minutes=15)
JOIN_LATE_WINDOW = timedelta(minutes=30)
PAYOUT_REVIEW_WINDOW = timedelta(hours=24)


def _get_booking_for_participant(request, pk):
    booking = get_object_or_404(
        Booking.objects.select_related(
            'student',
            'timeslot__course__teacher',
            'timeslot__course',
        ),
        pk=pk,
    )
    teacher = booking.timeslot.course.teacher
    if request.user.id not in (booking.student_id, teacher.id):
        return booking, HttpResponseForbidden('You are not a participant in this tutoring session.')
    return booking, None


def _session_link(booking):
    return reverse('course:tutoring_session', args=[booking.pk])


def _notify_once(user, title, message, link):
    notification, _ = Notification.objects.get_or_create(
        user=user,
        title=title,
        link=link,
        defaults={'message': message},
    )
    return notification


def _can_enter_session(booking):
    if booking.status != 'confirmed' or booking.is_refunded:
        return False
    now = timezone.now()
    return (
        booking.timeslot.start_time - JOIN_EARLY_WINDOW
        <= now
        <= booking.timeslot.end_time + JOIN_LATE_WINDOW
    )


def _active_attendance(booking, user):
    now = timezone.now()
    attendance = (
        SessionAttendance.objects
        .filter(booking=booking, user=user, left_at__isnull=True)
        .order_by('-joined_at')
        .first()
    )
    if attendance and attendance.last_seen_at < now - PRESENCE_TIMEOUT:
        attendance.left_at = attendance.last_seen_at
        attendance.save(update_fields=['left_at'])
        return None
    return attendance


def _calculate_shared_minutes(booking):
    teacher = booking.timeslot.course.teacher
    student_records = list(
        booking.attendance_records.filter(user=booking.student).order_by('joined_at')
    )
    teacher_records = list(
        booking.attendance_records.filter(user=teacher).order_by('joined_at')
    )

    now = timezone.now()
    total_seconds = 0

    for student_record in student_records:
        student_end = student_record.left_at or min(student_record.last_seen_at, now)
        for teacher_record in teacher_records:
            teacher_end = teacher_record.left_at or min(teacher_record.last_seen_at, now)
            overlap_start = max(student_record.joined_at, teacher_record.joined_at)
            overlap_end = min(student_end, teacher_end)
            if overlap_end > overlap_start:
                total_seconds += (overlap_end - overlap_start).total_seconds()

    return max(int(total_seconds // 60), 0)


def _update_session_state(booking):
    previous_status = booking.session_status
    shared_minutes = _calculate_shared_minutes(booking)
    booking.shared_minutes = shared_minutes

    if booking.is_test_booking:
        required_minutes = 1
    else:
        required_minutes = max(int((booking.timeslot.course.duration_minutes or 60) * 0.75), 10)

    teacher = booking.timeslot.course.teacher
    teacher_present = booking.attendance_records.filter(user=teacher).exists()
    student_present = booking.attendance_records.filter(user=booking.student).exists()

    if teacher_present and student_present and booking.session_started_at is None:
        booking.session_started_at = timezone.now()

    if shared_minutes >= required_minutes and booking.session_status != 'disputed':
        if booking.session_completed_at is None:
            booking.session_completed_at = timezone.now()
        booking.session_status = 'completed'
        if not booking.student_reported_issue and booking.payout_status == 'pending':
            booking.payout_status = 'awaiting_release'
            booking.payout_eligible_at = timezone.now() + PAYOUT_REVIEW_WINDOW
    elif teacher_present and student_present and booking.session_status == 'scheduled':
        booking.session_status = 'in_progress'

    booking.save(update_fields=[
        'shared_minutes',
        'session_started_at',
        'session_completed_at',
        'session_status',
        'payout_status',
        'payout_eligible_at',
    ])

    if previous_status != 'completed' and booking.session_status == 'completed':
        link = _session_link(booking)
        title = f'Tutoring Session Completed #{booking.pk}'
        if booking.is_test_booking:
            student_message = 'Your TEST tutoring session is complete. This test booking can never release real Stripe funds.'
            teacher_message = 'Your TEST tutoring session is complete. This test booking can never release real Stripe funds.'
        else:
            student_message = 'Your tutoring session is complete. You have 24 hours to report a problem before the teacher payment becomes eligible for release.'
            teacher_message = 'Your tutoring session is complete. The payment is now in the 24-hour student review period.'
        _notify_once(booking.student, title, student_message, link)
        _notify_once(teacher, title, teacher_message, link)


@login_required(login_url='my_login')
def tutoring_session(request, pk):
    booking, forbidden = _get_booking_for_participant(request, pk)
    if forbidden:
        return forbidden

    if booking.status != 'confirmed' or booking.is_refunded:
        return HttpResponseForbidden('This tutoring session is not available.')

    if not booking.meeting_room_id:
        booking.meeting_room_id = f'pandaspeak-{uuid.uuid4().hex}'
        booking.save(update_fields=['meeting_room_id'])

    teacher = booking.timeslot.course.teacher
    can_enter = _can_enter_session(booking)
    return render(request, 'course/tutoring_session.html', {
        'booking': booking,
        'teacher': teacher,
        'can_enter': can_enter,
        'is_teacher': request.user.id == teacher.id,
    })


@login_required(login_url='my_login')
@require_POST
def session_join(request, pk):
    booking, forbidden = _get_booking_for_participant(request, pk)
    if forbidden:
        return forbidden
    if not _can_enter_session(booking):
        return JsonResponse({'success': False, 'error': 'Session is outside the allowed join window.'}, status=403)

    attendance = _active_attendance(booking, request.user)
    created = attendance is None
    if created:
        attendance = SessionAttendance.objects.create(
            booking=booking,
            user=request.user,
            last_seen_at=timezone.now(),
        )
    else:
        attendance.last_seen_at = timezone.now()
        attendance.save(update_fields=['last_seen_at'])

    if created:
        teacher = booking.timeslot.course.teacher
        other_user = booking.student if request.user.id == teacher.id else teacher
        participant_name = request.user.get_full_name() or request.user.email
        _notify_once(
            other_user,
            f'Participant Joined Session #{booking.pk}',
            f'{participant_name} has joined your tutoring session.',
            _session_link(booking),
        )

    _update_session_state(booking)
    return JsonResponse({'success': True, 'attendance_id': attendance.id})


@login_required(login_url='my_login')
@require_POST
def session_heartbeat(request, pk):
    booking, forbidden = _get_booking_for_participant(request, pk)
    if forbidden:
        return forbidden

    attendance = _active_attendance(booking, request.user)
    if attendance is None:
        return JsonResponse({'success': False, 'error': 'No active attendance record.'}, status=409)

    attendance.last_seen_at = timezone.now()
    attendance.save(update_fields=['last_seen_at'])
    _update_session_state(booking)
    return JsonResponse({'success': True})


@login_required(login_url='my_login')
@require_POST
def session_leave(request, pk):
    booking, forbidden = _get_booking_for_participant(request, pk)
    if forbidden:
        return forbidden

    attendance = _active_attendance(booking, request.user)
    if attendance:
        now = timezone.now()
        attendance.last_seen_at = now
        attendance.left_at = now
        attendance.save(update_fields=['last_seen_at', 'left_at'])

    _update_session_state(booking)
    return JsonResponse({
        'success': True,
        'session_status': booking.session_status,
        'shared_minutes': booking.shared_minutes,
    })


@login_required(login_url='my_login')
def report_session_issue(request, pk):
    booking = get_object_or_404(
        Booking.objects.select_related('student', 'timeslot__course__teacher'),
        pk=pk,
        student=request.user,
    )

    if booking.session_status not in ('completed', 'disputed'):
        messages.error(request, 'A problem can be reported only after the tutoring session is completed.')
        return redirect('course:my_bookings')

    if booking.payout_status == 'transferred':
        messages.error(request, 'This teacher payment has already been released. Please contact PandaSpeak Support for assistance.')
        return redirect('course:my_bookings')

    if booking.payout_eligible_at and timezone.now() > booking.payout_eligible_at and not booking.student_reported_issue:
        messages.error(request, 'The 24-hour session review period has ended. Please contact PandaSpeak Support for assistance.')
        return redirect('course:my_bookings')

    if request.method == 'POST':
        details = (request.POST.get('issue_details') or '').strip()
        if len(details) < 10:
            messages.error(request, 'Please briefly describe the problem so PandaSpeak can review it.')
        else:
            booking.student_reported_issue = True
            booking.issue_details = details
            booking.issue_reported_at = timezone.now()
            booking.session_status = 'disputed'
            booking.payout_status = 'on_hold'
            booking.save(update_fields=[
                'student_reported_issue',
                'issue_details',
                'issue_reported_at',
                'session_status',
                'payout_status',
            ])

            teacher = booking.timeslot.course.teacher
            link = reverse('course:teacher_bookings')
            _notify_once(
                teacher,
                f'Tutoring Payment On Hold #{booking.pk}',
                'The student reported a problem with this tutoring session. The teacher payment has been placed on hold while PandaSpeak reviews it.',
                link,
            )

            User = get_user_model()
            for manager in User.objects.filter(is_staff=True, is_active=True):
                _notify_once(
                    manager,
                    f'Tutoring Session Needs Review #{booking.pk}',
                    f'{booking.student.get_full_name() or booking.student.email} reported a problem: {details[:250]}',
                    link,
                )

            messages.success(request, 'Your report was submitted. The teacher payment is now on hold while PandaSpeak reviews the session.')
            return redirect('course:my_bookings')

    return render(request, 'course/report_session_issue.html', {'booking': booking})
