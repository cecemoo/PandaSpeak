"""Meeting-room tests for course.session_views.

Covers one-on-one and group (one-on-multiple) tutoring sessions:
access control, shared/private room names, join window, teacher group
join/leave fan-out, and JaaS JWT on/off behaviour.
"""
import base64
import json
import os
from datetime import timedelta
from unittest import mock

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import timezone

from account.models import CustomUser

from .models import Booking, Course, SessionAttendance, TimeSlot


def _make_rsa_pem():
    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    return key.private_bytes(
        serialization.Encoding.PEM,
        serialization.PrivateFormat.PKCS8,
        serialization.NoEncryption(),
    ).decode()


def _decode_jwt_payload(jwt):
    payload_b64 = jwt.split('.')[1]
    payload_b64 += '=' * (-len(payload_b64) % 4)
    return json.loads(base64.urlsafe_b64decode(payload_b64))


class MeetingRoomTests(TestCase):
    def setUp(self):
        self.teacher = CustomUser.objects.create_user(
            email='teacher@example.com', password='pw', first_name='Tess', last_name='Teacher', is_teacher=True)
        self.student = CustomUser.objects.create_user(
            email='amy@example.com', password='pw', first_name='Amy', last_name='Chen')
        self.student2 = CustomUser.objects.create_user(
            email='ben@example.com', password='pw', first_name='Ben', last_name='Lin')
        self.outsider = CustomUser.objects.create_user(
            email='out@example.com', password='pw', first_name='Ollie', last_name='Out')

        now = timezone.now()
        self.start = now - timedelta(minutes=5)
        self.end = now + timedelta(minutes=55)

    def _course(self, session_type='private'):
        return Course.objects.create(
            teacher=self.teacher, title=f'{session_type} course', description='d',
            price=2000, duration_minutes=60, session_type=session_type,
            max_students=4 if session_type == 'group' else 1)

    def _booking(self, course, student, start=None, end=None, **kw):
        slot = kw.pop('slot', None)
        if slot is None:
            slot = TimeSlot.objects.create(
                course=course, start_time=start or self.start,
                end_time=end or self.end, capacity=course.max_students)
        kw.setdefault('status', 'confirmed')
        return Booking.objects.create(
            student=student, timeslot=slot,
            paid_at=timezone.now(), **kw), slot

    # --- one-on-one -----------------------------------------------------
    def test_private_student_and_teacher_share_one_stable_room(self):
        course = self._course('private')
        booking, _ = self._booking(course, self.student)
        self.client.force_login(self.student)
        r1 = self.client.get(reverse('course:tutoring_session', args=[booking.pk]))
        self.assertEqual(r1.status_code, 200)
        room1 = r1.context['meeting_room_id']
        self.assertTrue(room1.startswith('pandaspeak-'))
        self.client.force_login(self.teacher)
        r2 = self.client.get(reverse('course:tutoring_session', args=[booking.pk]))
        self.assertEqual(r2.context['meeting_room_id'], room1)

    def test_private_outsider_gets_403(self):
        course = self._course('private')
        booking, _ = self._booking(course, self.student)
        self.client.force_login(self.outsider)
        r = self.client.get(reverse('course:tutoring_session', args=[booking.pk]))
        self.assertEqual(r.status_code, 403)

    def test_private_join_outside_window_is_403(self):
        course = self._course('private')
        booking, _ = self._booking(
            course, self.student,
            start=timezone.now() + timedelta(hours=3),
            end=timezone.now() + timedelta(hours=4))
        self.client.force_login(self.student)
        r = self.client.post(reverse('course:session_join', args=[booking.pk]))
        self.assertEqual(r.status_code, 403)

    def test_private_join_and_leave_in_window(self):
        course = self._course('private')
        booking, _ = self._booking(course, self.student)
        self.client.force_login(self.student)
        r = self.client.post(reverse('course:session_join', args=[booking.pk]))
        self.assertEqual(r.status_code, 200)
        self.assertTrue(SessionAttendance.objects.filter(booking=booking, user=self.student).exists())
        r = self.client.post(reverse('course:session_leave', args=[booking.pk]))
        self.assertEqual(r.status_code, 200)

    def test_cancelled_booking_is_forbidden(self):
        course = self._course('private')
        booking, _ = self._booking(course, self.student, status='canceled')
        self.client.force_login(self.student)
        r = self.client.get(reverse('course:tutoring_session', args=[booking.pk]))
        self.assertEqual(r.status_code, 403)

    # --- group (one-on-multiple) ---------------------------------------
    def test_group_students_share_the_slot_room(self):
        course = self._course('group')
        b1, slot = self._booking(course, self.student)
        b2, _ = self._booking(course, self.student2, slot=slot)
        rooms = []
        for student, booking in ((self.student, b1), (self.student2, b2), (self.teacher, b1)):
            self.client.force_login(student)
            r = self.client.get(reverse('course:tutoring_session', args=[booking.pk]))
            self.assertEqual(r.status_code, 200)
            rooms.append(r.context['meeting_room_id'])
            self.assertEqual(r.context['group_booking_count'], 2)
        self.assertEqual(len(set(rooms)), 1)
        self.assertEqual(rooms[0], f'pandaspeak-group-slot-{slot.pk}')

    def test_group_unbooked_student_gets_403(self):
        course = self._course('group')
        b1, slot = self._booking(course, self.student)
        self._booking(course, self.student2, slot=slot)
        self.client.force_login(self.outsider)
        r = self.client.get(reverse('course:tutoring_session', args=[b1.pk]))
        self.assertEqual(r.status_code, 403)

    def test_group_teacher_join_creates_attendance_for_every_booking(self):
        course = self._course('group')
        b1, slot = self._booking(course, self.student)
        b2, _ = self._booking(course, self.student2, slot=slot)
        self.client.force_login(self.teacher)
        r = self.client.post(reverse('course:session_join', args=[b1.pk]))
        self.assertEqual(r.status_code, 200)
        for b in (b1, b2):
            self.assertTrue(
                SessionAttendance.objects.filter(booking=b, user=self.teacher).exists(),
                f'teacher attendance missing for booking {b.pk}')

    def test_group_student_join_only_touches_own_booking(self):
        course = self._course('group')
        b1, slot = self._booking(course, self.student)
        b2, _ = self._booking(course, self.student2, slot=slot)
        self.client.force_login(self.student)
        r = self.client.post(reverse('course:session_join', args=[b1.pk]))
        self.assertEqual(r.status_code, 200)
        self.assertTrue(SessionAttendance.objects.filter(booking=b1, user=self.student).exists())
        self.assertFalse(SessionAttendance.objects.filter(booking=b2, user=self.student).exists())

    # --- JaaS ------------------------------------------------------------
    def test_no_jaas_env_falls_back_cleanly(self):
        course = self._course('private')
        booking, _ = self._booking(course, self.student)
        self.client.force_login(self.student)
        with mock.patch.dict(os.environ, {}, clear=False):
            for k in ('JAAS_APP_ID', 'JAAS_API_KEY_ID', 'JAAS_PRIVATE_KEY', 'JAAS_PRIVATE_KEY_PATH'):
                os.environ.pop(k, None)
            r = self.client.get(reverse('course:tutoring_session', args=[booking.pk]))
        self.assertEqual(r.status_code, 200)
        self.assertFalse(r.context['jaas_enabled'])

    def test_jaas_env_produces_jwt_with_moderator_flag_for_teacher_only(self):
        course = self._course('private')
        booking, _ = self._booking(course, self.student)
        env = {
            'JAAS_APP_ID': 'test-app-id',
            'JAAS_API_KEY_ID': 'test-key-id',
            'JAAS_PRIVATE_KEY': _make_rsa_pem(),
            'JAAS_PRIVATE_KEY_PATH': '',
        }
        with mock.patch.dict(os.environ, env):
            self.client.force_login(self.student)
            r = self.client.get(reverse('course:tutoring_session', args=[booking.pk]))
            self.assertTrue(r.context['jaas_enabled'])
            payload = _decode_jwt_payload(r.context['jaas_jwt'])
            self.assertEqual(payload['context']['user']['moderator'], 'false')
            self.assertEqual(payload['sub'], 'test-app-id')
            self.client.force_login(self.teacher)
            r = self.client.get(reverse('course:tutoring_session', args=[booking.pk]))
            payload = _decode_jwt_payload(r.context['jaas_jwt'])
            self.assertEqual(payload['context']['user']['moderator'], 'true')

    def test_jaas_malformed_private_key_falls_back_instead_of_500(self):
        course = self._course('private')
        booking, _ = self._booking(course, self.student)
        env = {
            'JAAS_APP_ID': 'test-app-id',
            'JAAS_API_KEY_ID': 'test-key-id',
            'JAAS_PRIVATE_KEY': 'not-a-real-pem',
            'JAAS_PRIVATE_KEY_PATH': '',
        }
        with mock.patch.dict(os.environ, env):
            self.client.force_login(self.student)
            r = self.client.get(reverse('course:tutoring_session', args=[booking.pk]))
        self.assertEqual(r.status_code, 200)
        self.assertFalse(r.context['jaas_enabled'])
