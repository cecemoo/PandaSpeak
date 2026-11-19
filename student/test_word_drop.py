"""Tests for the Word Drop falling-word game."""
from decimal import Decimal

from django.test import TestCase
from django.urls import reverse

from account.models import CustomUser
from subscription.models import Subscription
from teacher.models import Idiom, Vocabulary


def _subscriber(email, level='level1'):
    user = CustomUser.objects.create_user(
        email=email, password='<redacted>', first_name='Pat', last_name='Student')
    user.learning_level = level
    user.save()
    Subscription.objects.create(
        user=user, subscription_plan='Base', subscription_cost=Decimal('15.00'), is_active=True)
    return user


def _seed_materials(level='level1', count=10):
    for n in range(count):
        Vocabulary.objects.create(
            word=f'詞{n}', pinyin=f'ci{n}', english_translation=f'word {n}',
            meaning=f'word {n}', level=level, visibility='all')
    Idiom.objects.create(
        idiom='胸有成竹', pinyin='xiong you cheng zhu',
        english_translation='having a plan in mind', meaning='having a plan in mind',
        level=level, visibility='all')


class WordDropPageTests(TestCase):
    def setUp(self):
        self.user = _subscriber('dropper@example.com')
        _seed_materials()
        self.client.force_login(self.user)

    def test_page_loads_with_game_markup(self):
        response = self.client.get(reverse('word_drop'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'wd-sky')
        self.assertContains(response, 'Word Drop')
        self.assertContains(response, 'panda-assistant.png')

    def test_items_endpoint_returns_level_materials(self):
        response = self.client.get(reverse('word_drop_items'))
        self.assertEqual(response.status_code, 200)
        data = response.json()
        texts = {item['text'] for item in data['items']}
        self.assertIn('胸有成竹', texts)
        self.assertTrue(any(item['kind'] == 'word' for item in data['items']))
        self.assertTrue(all(item['meaning'] for item in data['items']))

    def test_items_endpoint_404_when_too_few_materials(self):
        response = self.client.get(reverse('word_drop_items') + '?level=level3')
        self.assertEqual(response.status_code, 404)


class WordDropAccessTests(TestCase):
    def test_anonymous_is_redirected_to_login(self):
        response = self.client.get(reverse('word_drop'))
        self.assertEqual(response.status_code, 302)

    def test_non_subscriber_is_blocked(self):
        user = CustomUser.objects.create_user(
            email='free@example.com', password='<redacted>', first_name='Free', last_name='User')
        self.client.force_login(user)
        response = self.client.get(reverse('word_drop'))
        self.assertNotEqual(response.status_code, 200)
