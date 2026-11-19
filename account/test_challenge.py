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
        self.assertContains(response, reverse('challenge_next'))

    def test_homepage_widget_links_to_login_and_register(self):
        response = self.client.get(reverse('home'))
        self.assertContains(response, reverse('my_login'))
        self.assertContains(response, reverse('register'))
        self.assertContains(response, 'Register an account')


class ChallengeNextTests(TestCase):
    def _next(self, ip='203.0.113.7'):
        return self.client.post(reverse('challenge_next'), data='{}',
                                content_type='application/json', REMOTE_ADDR=ip)

    def test_returns_question_with_four_choices_including_answer(self):
        response = self._next()
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(len(data['choices']), 4)
        self.assertIn(data['answer'], data['choices'])
        self.assertTrue(data['text'] and data['zhuyin'] and data['pinyin'])

    def test_same_ip_never_repeats_until_bank_cycles(self):
        seen = [self._next().json()['text'] for _ in range(len(CHALLENGE_ITEMS))]
        self.assertEqual(len(seen), len(set(seen)))
        self.assertEqual(set(seen), {i['text'] for i in CHALLENGE_ITEMS})
        # After the full cycle, the next question starts a fresh cycle.
        self.assertIn(self._next().json()['text'], seen)

    def test_different_ip_has_independent_cycle(self):
        first = self._next('203.0.113.7').json()['text']
        other = self._next('198.51.100.23').json()['text']
        self.assertTrue(other)  # independent tracking; may or may not equal first
        self.assertNotEqual(self._next('198.51.100.23').json()['text'], other)
        self.assertNotEqual(self._next('203.0.113.7').json()['text'], first)

    def test_get_is_not_allowed(self):
        self.assertEqual(self.client.get(reverse('challenge_next')).status_code, 405)
