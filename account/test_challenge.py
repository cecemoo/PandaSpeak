"""Tests for the homepage 60-Second Chinese Challenge widget and its bank."""
from django.test import TestCase
from django.urls import reverse

from .challenge_data import CHALLENGE_ITEMS


class ChallengeBankTests(TestCase):
    def test_bank_has_words_and_idioms(self):
        words = [i for i in CHALLENGE_ITEMS if i['kind'] == 'word']
        idioms = [i for i in CHALLENGE_ITEMS if i['kind'] == 'idiom']
        self.assertGreaterEqual(len(words), 12)
        self.assertGreaterEqual(len(idioms), 30)

    def test_every_item_is_complete(self):
        for item in CHALLENGE_ITEMS:
            for field in ('text', 'pinyin', 'zhuyin', 'answer', 'kind'):
                self.assertTrue(str(item[field]).strip(), f'{item} missing {field}')

    def test_answers_unique_within_kind_so_distractors_are_valid(self):
        for kind in ('word', 'idiom'):
            answers = [i['answer'] for i in CHALLENGE_ITEMS if i['kind'] == kind]
            self.assertEqual(len(answers), len(set(answers)), kind)
            self.assertGreaterEqual(len(answers), 4, kind)


class ChallengeWidgetTests(TestCase):
    def test_homepage_shows_orange_challenge_bubble_and_popup(self):
        response = self.client.get(reverse('home'))
        self.assertContains(response, 'id="ps-ch-bubble"')
        self.assertContains(response, '60-Second Challenge')
        self.assertContains(response, 'Begin the Challenge')
        self.assertContains(response, 'ps-challenge-items')

    def test_homepage_widget_links_to_login_and_register(self):
        response = self.client.get(reverse('home'))
        self.assertContains(response, reverse('my_login'))
        self.assertContains(response, reverse('register'))
        self.assertContains(response, 'Register an account')
