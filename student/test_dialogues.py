"""Tests for the Dialogue listening practice (categories, topics, play page)."""
from decimal import Decimal

from django.test import SimpleTestCase, TestCase
from django.urls import reverse

from account.models import CustomUser
from student.dialogue_data import CATEGORIES, TOPICS
from student.models import DialogueFreePlay
from subscription.models import Subscription


def _subscriber(email, level='level2'):
    user = CustomUser.objects.create_user(
        email=email, password='<redacted>', first_name='Pat', last_name='Student')
    user.learning_level = level
    user.save()
    Subscription.objects.create(
        user=user, subscription_plan='Base', subscription_cost=Decimal('15.00'),
        is_active=True)
    return user


def _plus_subscriber(email, level='level2'):
    user = _subscriber(email, level)
    subscription = user.subscription
    subscription.plus_is_active = True
    subscription.save()
    return user


class DialogueDataTests(SimpleTestCase):
    def test_slugs_unique_and_categories_valid(self):
        category_slugs = {c['slug'] for c in CATEGORIES}
        seen = set()
        for topic in TOPICS:
            self.assertNotIn(topic['slug'], seen)
            seen.add(topic['slug'])
            self.assertIn(topic['category'], category_slugs)

    def test_every_topic_has_both_levels_fully_formed(self):
        for topic in TOPICS:
            for level in ('level2', 'level3'):
                version = topic['versions'][level]
                self.assertGreaterEqual(len(version['lines']), 8, topic['slug'])
                for speaker_key, text in version['lines']:
                    self.assertIn(speaker_key, topic['speakers'], topic['slug'])
                    self.assertTrue(text.strip(), topic['slug'])
                self.assertEqual(len(version['questions']), 4, topic['slug'])
                for question in version['questions']:
                    self.assertEqual(len(question['options']), 4, topic['slug'])
                    self.assertGreaterEqual(question['answer'], 0)
                    self.assertLess(question['answer'], 4)

    def test_speakers_have_voice_speed_and_style(self):
        for topic in TOPICS:
            self.assertEqual(len(topic['speakers']), 2, topic['slug'])
            for speaker in topic['speakers'].values():
                self.assertTrue(speaker['voice'])
                self.assertTrue(speaker['style'])
                self.assertGreater(speaker['speed'], 0.5)
                self.assertLess(speaker['speed'], 1.5)


class DialoguePageTests(TestCase):
    def test_level1_sees_locked_categories_and_no_play_page(self):
        self.client.force_login(_subscriber('dlg-l1@example.com', 'level1'))
        response = self.client.get(reverse('dialogue_categories'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Available at Level II')
        play = self.client.get(reverse('dialogue_play', args=['busy-morning']))
        self.assertEqual(play.status_code, 404)

    def test_level2_browses_categories_topics_and_plays(self):
        self.client.force_login(_subscriber('dlg-l2@example.com', 'level2'))
        response = self.client.get(reverse('dialogue_categories'))
        self.assertContains(response, 'Daily Life')
        self.assertContains(response, 'Work, School &amp; Social')
        topics = self.client.get(reverse('dialogue_topics', args=['daily-life']))
        self.assertContains(topics, 'A Busy Morning')
        self.assertContains(topics, 'Asking a Neighbor for Help')
        play = self.client.get(reverse('dialogue_play', args=['busy-morning']))
        self.assertEqual(play.status_code, 200)
        self.assertContains(play, 'busy-morning-l2.mp3')
        self.assertContains(play, 'dlg-questions-data')
        self.assertContains(play, 'What time is it when Mom wakes Xiao Jie?')

    def test_level3_gets_level3_audio(self):
        self.client.force_login(_subscriber('dlg-l3@example.com', 'level3'))
        play = self.client.get(reverse('dialogue_play', args=['busy-morning']))
        self.assertEqual(play.status_code, 200)
        self.assertContains(play, 'busy-morning-l3.mp3')

    def test_unknown_category_and_topic_404(self):
        self.client.force_login(_subscriber('dlg-l2b@example.com', 'level2'))
        self.assertEqual(
            self.client.get(reverse('dialogue_topics', args=['nope'])).status_code,
            404)
        self.assertEqual(
            self.client.get(reverse('dialogue_play', args=['nope'])).status_code,
            404)

    def test_non_plus_gets_one_free_dialogue_then_plus_gate(self):
        user = _subscriber('dlg-nonplus@example.com', 'level2')
        self.client.force_login(user)
        categories = self.client.get(reverse('dialogue_categories'))
        self.assertContains(categories, 'your first dialogue is free')
        first = self.client.get(reverse('dialogue_play', args=['busy-morning']))
        self.assertEqual(first.status_code, 200)
        self.assertContains(first, 'This is your free dialogue')
        free = DialogueFreePlay.objects.get(student=user)
        self.assertEqual(free.topic_slug, 'busy-morning')
        replay = self.client.get(reverse('dialogue_play', args=['busy-morning']))
        self.assertEqual(replay.status_code, 200)
        other = self.client.get(reverse('dialogue_play', args=['taking-a-taxi']))
        self.assertEqual(other.status_code, 302)
        self.assertTrue(other.url.endswith(reverse('plus_upgrade')))
        topics = self.client.get(reverse('dialogue_topics', args=['daily-life']))
        self.assertContains(topics, 'Your free dialogue')
        self.assertContains(topics, 'Your free dialogue is')

    def test_plus_student_plays_any_dialogue_without_claiming_free(self):
        user = _plus_subscriber('dlg-plus@example.com', 'level2')
        self.client.force_login(user)
        for slug in ('busy-morning', 'taking-a-taxi', 'at-the-bank'):
            response = self.client.get(reverse('dialogue_play', args=[slug]))
            self.assertEqual(response.status_code, 200, slug)
            self.assertNotContains(response, 'This is your free dialogue')
        self.assertFalse(DialogueFreePlay.objects.filter(student=user).exists())
        categories = self.client.get(reverse('dialogue_categories'))
        self.assertNotContains(categories, 'your first dialogue is free')

    def test_non_subscriber_is_redirected(self):
        user = CustomUser.objects.create_user(
            email='dlg-free@example.com', password='<redacted>',
            first_name='Free', last_name='User')
        user.learning_level = 'level2'
        user.save()
        self.client.force_login(user)
        response = self.client.get(reverse('dialogue_categories'))
        self.assertEqual(response.status_code, 302)
