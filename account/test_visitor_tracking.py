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
        self.assertContains(response, 'Panda assistant chats')
        self.assertContains(response, '60-sec challenge players')
        self.assertContains(response, 'Register page visits')
