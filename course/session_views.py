import base64
import json
import os
import uuid
from datetime import timedelta

from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
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
PAYOUT_REVIEW_WINDOW = timedelta(days=5)


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


def _is_group_booking(booking):
    return booking.timeslot.course.session_type == 'group'


def _group_bookings(booking):
    return list(
        Booking.objects
        .filter(
            timeslot=booking.timeslot,
            status='confirmed',
            is_refunded=False,
        )
        .select_related('student', 'timeslot__course__teacher', 'timeslot__course')
        .order_by('pk')
    )


def _room_name_for_booking(booking):
    if _is_group_booking(booking):
        return f'pandaspeak-group-slot-{booking.timeslot_id}'

    if not booking.meeting_room_id:
        booking.meeting_room_id = f'pandaspeak-{uuid.uuid4().hex}'
        booking.save(update_fields=['meeting_room_id'])
    return booking.meeting_room_id


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


def _touch_attendance(booking, user):
    attendance = _active_attendance(booking, user)
    created = attendance is None
    if created:
        attendance = SessionAttendance.objects.create(
            booking=booking,
            user=user,
            last_seen_at=timezone.now(),
        )
    else:
        attendance.last_seen_at = timezone.now()
        attendance.save(update_fields=['last_seen_at'])
    return attendance, created


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
            booking.payout_eligible_at = booking.timeslot.end_time + PAYOUT_REVIEW_WINDOW
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
            student_message = 'Your tutoring session is complete. You have five days after the scheduled session end time to report a problem before the teacher payment becomes eligible for release.'
            teacher_message = 'Your tutoring session is complete. The payment is now in the five-day student review period, calculated from the scheduled session end time.'
        _notify_once(booking.student, title, student_message, link)
        _notify_once(teacher, title, teacher_message, link)


def _b64url(data):
    return base64.urlsafe_b64encode(data).rstrip(b'=')


def _load_jaas_private_key():
    private_key_path = (os.getenv('JAAS_PRIVATE_KEY_PATH') or '').strip()
    if private_key_path:
        try:
            with open(private_key_path, 'r', encoding='utf-8') as key_file:
                return key_file.read().strip()
        except (OSError, UnicodeError):
            return ''

    return (os.getenv('JAAS_PRIVATE_KEY') or '').strip().replace('\\n', '\n')


def _create_jaas_jwt(user, room_name, is_teacher):
    app_id = (os.getenv('JAAS_APP_ID') or '').strip()
    api_key_id = (os.getenv('JAAS_API_KEY_ID') or '').strip()
    private_key_pem = _load_jaas_private_key()

    if not app_id or not api_key_id or not private_key_pem:
        return None

    now = int(timezone.now().timestamp())
    display_name = user.get_full_name() or user.email or user.username

    header = {
        'alg': 'RS256',
        'kid': api_key_id,
        'typ': 'JWT',
    }
    payload = {
        'aud': 'jitsi',
        'iss': 'chat',
        'sub': app_id,
        'room': room_name,
        'nbf': now - 10,
        'exp': now + 60 * 60 * 2,
        'context': {
            'user': {
                'id': str(user.pk),
                'name': display_name,
                'email': user.email or '',
                'moderator': 'true' if is_teacher else 'false',
            },
            'features': {
                'livestreaming': False,
                'outbound-call': False,
                'transcription': False,
                'recording': False,
            },
            'room': {
                'regex': False,
            },
        },
    }

    encoded_header = _b64url(json.dumps(header, separators=(',', ':')).encode())
    encoded_payload = _b64url(json.dumps(payload, separators=(',', ':')).encode())
    signing_input = encoded_header + b'.' + encoded_payload

    private_key = serialization.load_pem_private_key(
        private_key_pem.encode(),
        password=None,
    )
    signature = private_key.sign(
        signing_input,
        padding.PKCS1v15(),
        hashes.SHA256(),
    )
    return (signing_input + b'.' + _b64url(signature)).decode()


@login_required(login_url='my_login')
def tutoring_session(request, pk):
    booking, forbidden = _get_booking_for_participant(request, pk)
    if forbidden:
        return forbidden

    if booking.status != 'confirmed' or booking.is_refunded:
        return HttpResponseForbidden('This tutoring session is not available.')

    room_name = _room_name_for_booking(booking)
    teacher = booking.timeslot.course.teacher
    is_teacher = request.user.id == teacher.id
    can_enter = _can_enter_session(booking)

    group_bookings = _group_bookings(booking) if _is_group_booking(booking) else [booking]

    jaas_app_id = (os.getenv('JAAS_APP_ID') or '').strip()
    jaas_jwt = None
    if can_enter and jaas_app_id:
        try:
            jaas_jwt = _create_jaas_jwt(
                request.user,
                room_name,
                is_teacher,
            )
        except (ValueError, TypeError):
            jaas_jwt = None

    jaas_enabled = bool(jaas_app_id and jaas_jwt)
    return_url = reverse('teacher_dashboard') if is_teacher else reverse('student_dashboard')

    return render(request, 'course/tutoring_session.html', {
        'booking': booking,
        'teacher': teacher,
        'can_enter': can_enter,
        'is_teacher': is_teacher,
        'jaas_enabled': jaas_enabled,
        'jaas_app_id': jaas_app_id,
        'jaas_jwt': jaas_jwt,
        'return_url': return_url,
        'meeting_room_id': room_name,
        'group_booking_count': len(group_bookings),
    })


@login_required(login_url='my_login')
@require_POST
def session_join(request, pk):
    booking, forbidden = _get_booking_for_participant(request, pk)
    if forbidden:
        return forbidden
    if not _can_enter_session(booking):
        return JsonResponse({'success': False, 'error': 'Session is outside the allowed join window.'}, status=403)

    teacher = booking.timeslot.course.teacher
    participant_name = request.user.get_full_name() or request.user.email

    if _is_group_booking(booking) and request.user.id == teacher.id:
        primary_attendance = None
        for group_booking in _group_bookings(booking):
            attendance, created = _touch_attendance(group_booking, request.user)
            if primary_attendance is None:
                primary_attendance = attendance
            if created:
                _notify_once(
                    group_booking.student,
                    f'Teacher Joined Group Session #{group_booking.pk}',
                    f'{participant_name} has joined your group tutoring session.',
                    _session_link(group_booking),
                )
            _update_session_state(group_booking)
        return JsonResponse({
            'success': True,
            'attendance_id': primary_attendance.id if primary_attendance else None,
        })

    attendance, created = _touch_attendance(booking, request.user)
    if created:
        other_user = booking.student if request.user.id == teacher.id else teacher
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

    teacher = booking.timeslot.course.teacher
    if _is_group_booking(booking) and request.user.id == teacher.id:
        found_attendance = False
        for group_booking in _group_bookings(booking):
            attendance, _ = _touch_attendance(group_booking, request.user)
            if attendance:
                found_attendance = True
            _update_session_state(group_booking)
        if not found_attendance:
            return JsonResponse({'success': False, 'error': 'No active attendance record.'}, status=409)
        return JsonResponse({'success': True})

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

    teacher = booking.timeslot.course.teacher
    if _is_group_booking(booking) and request.user.id == teacher.id:
        now = timezone.now()
        for group_booking in _group_bookings(booking):
            attendance = _active_attendance(group_booking, request.user)
            if attendance:
                attendance.last_seen_at = now
                attendance.left_at = now
                attendance.save(update_fields=['last_seen_at', 'left_at'])
            _update_session_state(group_booking)
        booking.refresh_from_db(fields=['session_status', 'shared_minutes'])
        return JsonResponse({
            'success': True,
            'session_status': booking.session_status,
            'shared_minutes': booking.shared_minutes,
        })

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
def review_tutoring_session(request, pk):
    booking = get_object_or_404(
        Booking.objects.select_related('student', 'timeslot__course__teacher', 'timeslot__course'),
        pk=pk,
        student=request.user,
        status='confirmed',
        is_refunded=False,
    )

    if booking.session_status != 'completed':
        messages.error(request, 'You can review a tutoring session only after it is completed.')
        return redirect('student_dashboard')

    if booking.reviewed_at:
        messages.info(request, 'You already submitted a review for this tutoring session.')
        return redirect('student_dashboard')

    if request.method == 'POST':
        try:
            rating = int(request.POST.get('rating', ''))
        except (TypeError, ValueError):
            rating = 0
        comment = (request.POST.get('comment') or '').strip()

        if rating not in (1, 2, 3, 4, 5):
            messages.error(request, 'Please select a rating from 1 to 5 stars.')
        else:
            booking.review_rating = rating
            booking.review_comment = comment
            booking.reviewed_at = timezone.now()
            booking.save(update_fields=['review_rating', 'review_comment', 'reviewed_at'])

            teacher = booking.timeslot.course.teacher
            student_name = booking.student.get_full_name() or booking.student.email
            teacher_name = teacher.get_full_name() or teacher.email
            manager_link = reverse('manager_dashboard')
            review_message = (
                f'{student_name} rated the tutoring session with {teacher_name} '
                f'{rating}/5 stars.'
            )
            if comment:
                review_message += f' Review: {comment[:300]}'

            User = get_user_model()
            for manager in User.objects.filter(is_staff=True, is_active=True):
                Notification.objects.create(
                    user=manager,
                    title=f'New Tutoring Session Review #{booking.pk}',
                    message=review_message,
                    link=manager_link,
                )

            email_message = (
                f'A student submitted a tutoring session review on PandaSpeak.\n\n'
                f'Student: {student_name}\n'
                f'Teacher: {teacher_name}\n'
                f'Course: {booking.timeslot.course.title}\n'
                f'Session: {booking.timeslot.start_time:%b %d, %Y %I:%M %p}\n'
                f'Rating: {rating}/5\n'
                f'Review: {comment or "No written comment."}\n'
            )
            send_mail(
                subject=f'PandaSpeak Tutoring Review #{booking.pk} — {rating}/5 stars',
                message=email_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=['pandaspeaksupport@gmail.com'],
                fail_silently=True,
            )

            messages.success(request, 'Thank you. Your tutoring session review was submitted to PandaSpeak management.')
            return redirect('student_dashboard')

    return render(request, 'course/review_tutoring_session.html', {'booking': booking})


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

    review_deadline = booking.timeslot.end_time + PAYOUT_REVIEW_WINDOW
    if timezone.now() > review_deadline and not booking.student_reported_issue:
        messages.error(request, 'The five-day session review period has ended. Please contact PandaSpeak Support for assistance.')
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
