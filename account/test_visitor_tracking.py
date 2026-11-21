"""Tests for daily visitor counting and the dashboard visitor card."""
from datetime import timedelta

from django.core.cache import cache
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from account.models import CustomUser, DailyVisitor

BROWSER_UA = 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15'


class VisitorCountingTests(TestCase):
    def setUp(self):
        cache.clear()

    def tearDown(self):
        cache.clear()

    def test_anonymous_visit_counted_once_per_day(self):
        self.client.get(reverse('home'), HTTP_USER_AGENT=BROWSER_UA)
        self.client.get(reverse('home'), HTTP_USER_AGENT=BROWSER_UA)
        self.assertEqual(DailyVisitor.objects.count(), 1)

    def test_different_visitor_counted_separately(self):
        self.client.get(reverse('home'), HTTP_USER_AGENT=BROWSER_UA)
        self.client.get(reverse('home'), HTTP_USER_AGENT='Mozilla/5.0 (Windows NT 10.0) Chrome/120.0')
        self.assertEqual(DailyVisitor.objects.count(), 2)

    def test_bots_are_not_counted(self):
        self.client.get(reverse('home'), HTTP_USER_AGENT='Mozilla/5.0 (compatible; Googlebot/2.1)')
        self.assertEqual(DailyVisitor.objects.count(), 0)

    def test_staff_browsing_is_not_counted(self):
        staff = CustomUser.objects.create_user(
            email='boss@example.com', password='Str0ng!Passw0rd',
            first_name='Boss', last_name='User', is_staff=True)
        self.client.force_login(staff)
        self.client.get(reverse('home'), HTTP_USER_AGENT=BROWSER_UA)
        self.assertEqual(DailyVisitor.objects.count(), 0)

    def test_missing_pages_are_not_counted(self):
        self.client.get('/no-such-page-here/', HTTP_USER_AGENT=BROWSER_UA)
        self.assertEqual(DailyVisitor.objects.count(), 0)


class DashboardVisitorCardTests(TestCase):
    def setUp(self):
        cache.clear()
        today = timezone.localdate()
        DailyVisitor.objects.create(visitor_key='a' * 64, date=today)
        DailyVisitor.objects.create(visitor_key='b' * 64, date=today)
        DailyVisitor.objects.create(visitor_key='a' * 64, date=today - timedelta(days=3))
        DailyVisitor.objects.create(visitor_key='c' * 64, date=today - timedelta(days=40))
        manager = CustomUser.objects.create_user(
            email='manager@example.com', password='Str0ng!Passw0rd',
            first_name='Man', last_name='Ager', is_staff=True, is_superuser=True)
        self.client.force_login(manager)

    def tearDown(self):
        cache.clear()

    def test_dashboard_shows_visitor_counts(self):
        response = self.client.get(reverse('manager_dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['visitors_today'], 2)
        self.assertEqual(response.context['visitors_7d'], 2)
        self.assertEqual(response.context['visitors_30d'], 2)
        self.assertEqual(response.context['visitors_total'], 3)
        self.assertContains(response, 'Website Visitors')


import json

from account.models import VisitorAction


class VisitorActionTests(TestCase):
    def setUp(self):
        cache.clear()

    def tearDown(self):
        cache.clear()

    def test_register_page_view_recorded_once_per_day(self):
        self.client.get(reverse('register'), HTTP_USER_AGENT=BROWSER_UA)
        self.client.get(reverse('register'), HTTP_USER_AGENT=BROWSER_UA)
        self.assertEqual(
            VisitorAction.objects.filter(action='register_view').count(), 1)

    def test_help_chat_recorded_once_per_day(self):
        for _ in range(2):
            response = self.client.post(
                reverse('help_chat'),
                data=json.dumps({'message': 'How much does it cost?'}),
                content_type='application/json',
                HTTP_USER_AGENT=BROWSER_UA)
            self.assertEqual(response.status_code, 200)
        self.assertEqual(
            VisitorAction.objects.filter(action='help_chat').count(), 1)

    def test_challenge_play_recorded(self):
        response = self.client.post(
            reverse('challenge_next'), HTTP_USER_AGENT=BROWSER_UA)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            VisitorAction.objects.filter(action='challenge_play').count(), 1)

    def test_staff_actions_are_not_recorded(self):
        staff = CustomUser.objects.create_user(
            email='boss2@example.com', password='Str0ng!Passw0rd',
            first_name='Boss', last_name='User', is_staff=True)
        self.client.force_login(staff)
        self.client.post(
            reverse('help_chat'),
            data=json.dumps({'message': 'Testing it myself'}),
            content_type='application/json',
            HTTP_USER_AGENT=BROWSER_UA)
        self.client.get(reverse('register'), HTTP_USER_AGENT=BROWSER_UA)
        self.assertEqual(VisitorAction.objects.count(), 0)


class DashboardActionCardTests(TestCase):
    def setUp(self):
        cache.clear()
        today = timezone.localdate()
        VisitorAction.objects.create(visitor_key='a' * 64, action='help_chat', date=today)
        VisitorAction.objects.create(visitor_key='b' * 64, action='help_chat', date=today)
        VisitorAction.objects.create(visitor_key='a' * 64, action='challenge_play', date=today)
        VisitorAction.objects.create(visitor_key='a' * 64, action='challenge_play', date=today - timedelta(days=5))
        VisitorAction.objects.create(visitor_key='c' * 64, action='register_view', date=today)
        VisitorAction.objects.create(visitor_key='d' * 64, action='tutoring_view', date=today)
        VisitorAction.objects.create(visitor_key='d' * 64, action='course_detail_view', date=today)
        VisitorAction.objects.create(visitor_key='e' * 64, action='about_view', date=today)
        VisitorAction.objects.create(visitor_key='f' * 64, action='placement_test', date=today)
        manager = CustomUser.objects.create_user(
            email='manager2@example.com', password='Str0ng!Passw0rd',
            first_name='Man', last_name='Ager', is_staff=True, is_superuser=True)
        self.client.force_login(manager)

    def tearDown(self):
        cache.clear()

    def test_dashboard_shows_action_counts(self):
        response = self.client.get(reverse('manager_dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['assistant_today'], 2)
        self.assertEqual(response.context['assistant_total'], 2)
        self.assertEqual(response.context['challenge_players_today'], 1)
        self.assertEqual(response.context['challenge_players_total'], 1)
        self.assertEqual(response.context['register_views_today'], 1)
        self.assertEqual(response.context['register_views_total'], 1)
        self.assertEqual(response.context['tutoring_views_today'], 1)
        self.assertEqual(response.context['tutoring_views_total'], 1)
        self.assertEqual(response.context['course_detail_views_today'], 1)
        self.assertEqual(response.context['course_detail_views_total'], 1)
        self.assertEqual(response.context['about_views_today'], 1)
        self.assertEqual(response.context['about_views_total'], 1)
        self.assertEqual(response.context['placement_takers_today'], 1)
        self.assertEqual(response.context['placement_takers_total'], 1)
        self.assertContains(response, 'Panda assistant chats')
        self.assertContains(response, '60-sec challenge players')
        self.assertContains(response, 'Register page visits')
        self.assertContains(response, 'Tutoring page visits')
        self.assertContains(response, 'Course page visits')
        self.assertContains(response, 'About us visits')
        self.assertContains(response, 'Free placement test takers')


class PageViewTrackingTests(TestCase):
    def setUp(self):
        cache.clear()

    def tearDown(self):
        cache.clear()

    def test_tutoring_page_view_recorded_once_per_day(self):
        self.client.get(reverse('course:course_list'), HTTP_USER_AGENT=BROWSER_UA)
        self.client.get(reverse('course:course_list'), HTTP_USER_AGENT=BROWSER_UA)
        self.assertEqual(
            VisitorAction.objects.filter(action='tutoring_view').count(), 1)

    def test_about_page_view_recorded_once_per_day(self):
        self.client.get(reverse('about'), HTTP_USER_AGENT=BROWSER_UA)
        self.client.get(reverse('about'), HTTP_USER_AGENT=BROWSER_UA)
        self.assertEqual(
            VisitorAction.objects.filter(action='about_view').count(), 1)

    def test_course_detail_view_recorded_once_per_day(self):
        from course.models import Course
        teacher = CustomUser.objects.create_user(
            email='tutor@example.com', password='<redacted>',
            first_name='Tess', last_name='Teacher', is_teacher=True)
        course = Course.objects.create(
            teacher=teacher, title='Conversation course', description='d',
            price=2000, duration_minutes=60, session_type='private',
            max_students=1)
        url = reverse('course:course_detail', args=[course.pk])
        self.client.get(url, HTTP_USER_AGENT=BROWSER_UA)
        self.client.get(url, HTTP_USER_AGENT=BROWSER_UA)
        self.assertEqual(
            VisitorAction.objects.filter(action='course_detail_view').count(), 1)


class PlacementTestTrackingTests(TestCase):
    def setUp(self):
        cache.clear()
        from account.models import PlacementQuestion
        self.question = PlacementQuestion.objects.create(
            level='level1', prompt='What is this?',
            choice_a='Apple', choice_b='Banana', choice_c='Cat',
            choice_d='Dog', correct_answer='A', order=1)

    def tearDown(self):
        cache.clear()

    def test_viewing_the_test_page_does_not_count_as_taking_it(self):
        self.client.get(reverse('placement_test'), HTTP_USER_AGENT=BROWSER_UA)
        self.assertEqual(
            VisitorAction.objects.filter(action='placement_test').count(), 0)

    def test_completing_the_test_records_the_taker(self):
        response = self.client.post(
            reverse('placement_test'),
            {f'question_{self.question.id}': 'A'},
            HTTP_USER_AGENT=BROWSER_UA)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            VisitorAction.objects.filter(action='placement_test').count(), 1)
