"""Tests for per-level AI conversation topics and the livelier chat window."""
import uuid
from decimal import Decimal
from unittest.mock import patch

from django.test import TestCase
from django.urls import reverse

from account.models import CustomUser
from subscription.models import Subscription

from . import ai_conversation_views as views


def _subscriber(email):
    user = CustomUser.objects.create_user(
        email=email, password='<redacted>', first_name='Pat', last_name='Student')
    Subscription.objects.create(
        user=user, subscription_plan='Base', subscription_cost=Decimal('15.00'), is_active=True)
    return user


class TopicCatalogTests(TestCase):
    def test_each_level_has_at_least_twelve_topics(self):
        for level, topics in views.LEVEL_SCENARIOS.items():
            self.assertGreaterEqual(len(topics), 12, f'level {level}')

    def test_every_topic_has_a_greeting(self):
        for level, topics in views.LEVEL_SCENARIOS.items():
            for key in topics:
                self.assertIn(key, views.SCENARIO_GREETINGS, f'{key} (level {level})')
                self.assertTrue(views.SCENARIO_GREETINGS[key].strip())

    def test_levels_offer_different_topics(self):
        self.assertIn('daily_routine', views.LEVEL_SCENARIOS['1'])
        self.assertNotIn('daily_routine', views.LEVEL_SCENARIOS['3'])
        self.assertIn('current_events', views.LEVEL_SCENARIOS['3'])
        self.assertNotIn('current_events', views.LEVEL_SCENARIOS['1'])
        self.assertIn('transport', views.LEVEL_SCENARIOS['2'])


class ConversationPageTests(TestCase):
    def setUp(self):
        self.user = _subscriber('learner@example.com')
        self.client.force_login(self.user)

    def test_level_one_page_shows_level_one_topics_only(self):
        response = self.client.get(reverse('ai_conversation'))
        self.assertContains(response, 'Daily Routine 每日作息')
        self.assertContains(response, 'Pets &amp; Animals 寵物和動物')
        self.assertNotContains(response, 'Current Events 時事討論')

    def test_level_three_page_shows_level_three_topics_only(self):
        with patch.object(views, '_student_level', return_value='3'):
            response = self.client.get(reverse('ai_conversation'))
        self.assertContains(response, 'Current Events 時事討論')
        self.assertContains(response, 'Opinions &amp; Discussion 表達看法')
        self.assertNotContains(response, 'Daily Routine 每日作息')

    def test_page_has_panda_avatar_dots_and_sound_effects(self):
        response = self.client.get(reverse('ai_conversation'))
        self.assertContains(response, 'assets/img/panda-assistant.png')
        self.assertContains(response, 'ai-dots')
        self.assertContains(response, 'showTyping')
        self.assertContains(response, 'soundToggle')


class ReplyScenarioTests(TestCase):
    def setUp(self):
        self.user = _subscriber('talker@example.com')
        self.client.force_login(self.user)

    def _reply(self, scenario):
        return self.client.post(
            reverse('ai_conversation_reply'),
            data={'scenario': scenario, 'message': '你好', 'history': [],
                  'session_id': str(uuid.uuid4())},
            content_type='application/json')

    @patch.object(views, '_call_openai', return_value=('你好！很高興認識你。', 'test-model', 10, 5))
    def test_new_level_two_topic_is_accepted(self, _mock):
        response = self._reply('transport')
        self.assertEqual(response.status_code, 200)
        self.assertIn('reply', response.json())

    @patch.object(views, '_call_openai', return_value=('你好！', 'test-model', 10, 5))
    def test_new_level_three_topic_is_accepted(self, _mock):
        response = self._reply('current_events')
        self.assertEqual(response.status_code, 200)

    def test_unknown_scenario_is_rejected(self):
        response = self._reply('not_a_topic')
        self.assertEqual(response.status_code, 400)
