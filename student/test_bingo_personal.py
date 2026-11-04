"""Tests for student-created personal Bingo games.

Covers the "Create Your Own Bingo" flow on the student Bingo page:
creating a personal game from a content type / category / subcategory /
level selection, who can see and play it, the subcategory filter on
eligible materials, and deleting a personal game.
"""
from decimal import Decimal

from django.test import TestCase
from django.urls import reverse

from account.models import CustomUser
from subscription.models import Subscription
from teacher.bingo_models import BingoGame
from teacher.models import Vocabulary, VocabularyCategory

from .bingo_views import _bingo_creation_options, _eligible_materials


def _subscriber(email, first_name='Pat'):
    user = CustomUser.objects.create_user(
        email=email, password='<redacted>', first_name=first_name, last_name='Student')
    Subscription.objects.create(
        user=user, subscription_plan='Base', subscription_cost=Decimal('15.00'), is_active=True)
    return user


def _vocabulary(category, word, subcategory='', level='level1'):
    return Vocabulary.objects.create(
        word=word,
        meaning=f'meaning of {word}',
        audio_file='vocab/test.mp3',
        category=category,
        subcategory=subcategory,
        level=level,
    )


class PersonalBingoTests(TestCase):
    def setUp(self):
        self.creator = _subscriber('creator@example.com', 'Cara')
        self.other = _subscriber('other@example.com', 'Omar')
        self.category = VocabularyCategory.objects.create(category_name='numbers')
        for i in range(9):
            _vocabulary(self.category, f'word-{i}')

    def _create_via_view(self, user, **overrides):
        data = {
            'content_type': 'vocabulary',
            'category_id': str(self.category.id),
            'subcategory': '',
            'level': 'level1',
        }
        data.update(overrides)
        self.client.force_login(user)
        return self.client.post(reverse('create_personal_bingo'), data)

    def test_create_valid_selection_makes_personal_game_and_redirects_to_play(self):
        response = self._create_via_view(self.creator, subcategory='')
        game = BingoGame.objects.get(audience='personal')
        self.assertEqual(game.teacher, self.creator)
        self.assertEqual(game.title, 'numbers')
        self.assertEqual(game.content_type, 'vocabulary')
        self.assertEqual(game.category_key, f'vocabulary:{self.category.id}')
        self.assertEqual(game.subcategory, '')
        self.assertEqual(game.level, 'level1')
        self.assertEqual(game.game_mode, 'listening')
        self.assertIsNone(game.student_group)
        self.assertFalse(game.adaptive_difficulty)
        self.assertTrue(game.use_free_center)
        self.assertTrue(game.is_active)
        self.assertRedirects(response, reverse('play_bingo', args=[game.id]))

    def test_create_ignores_posted_subcategory(self):
        # The create form no longer offers a subcategory (removed 2026-11-03 at
        # Cece's direction); a posted subcategory must not narrow the game.
        for i in range(9):
            _vocabulary(self.category, f'greeting-{i}', subcategory='greetings')
        response = self._create_via_view(self.creator, subcategory='greetings')
        game = BingoGame.objects.get(audience='personal')
        self.assertEqual(game.subcategory, '')
        self.assertEqual(game.title, 'numbers')
        self.assertRedirects(response, reverse('play_bingo', args=[game.id]))

    def test_create_with_too_few_materials_creates_nothing(self):
        small = VocabularyCategory.objects.create(category_name='colors')
        for i in range(3):
            _vocabulary(small, f'color-{i}')
        response = self._create_via_view(self.creator, category_id=str(small.id))
        self.assertEqual(BingoGame.objects.count(), 0)
        self.assertRedirects(response, reverse('student_bingo_list'))

    def test_create_get_redirects_to_list(self):
        self.client.force_login(self.creator)
        response = self.client.get(reverse('create_personal_bingo'))
        self.assertRedirects(response, reverse('student_bingo_list'))

    def test_personal_game_visible_only_to_its_creator(self):
        self._create_via_view(self.creator)
        game = BingoGame.objects.get(audience='personal')

        self.client.force_login(self.creator)
        creator_list = self.client.get(reverse('student_bingo_list'))
        self.assertEqual([g.id for g in creator_list.context['games']], [game.id])
        self.assertContains(creator_list, game.title)

        self.client.force_login(self.other)
        other_list = self.client.get(reverse('student_bingo_list'))
        self.assertEqual(list(other_list.context['games']), [])

        play_response = self.client.get(reverse('play_bingo', args=[game.id]))
        self.assertRedirects(play_response, reverse('student_bingo_list'))

    def test_eligible_materials_respects_subcategory(self):
        for i in range(4):
            _vocabulary(self.category, f'greet-{i}', subcategory='greetings')
        for i in range(5):
            _vocabulary(self.category, f'bye-{i}', subcategory='farewells')
        probe = BingoGame(
            teacher=self.creator,
            title='probe',
            audience='personal',
            content_type='vocabulary',
            category_key=f'vocabulary:{self.category.id}',
            subcategory='greetings',
            level='level1',
        )
        materials = _eligible_materials(probe, 'level1')
        self.assertEqual(materials.count(), 4)
        self.assertTrue(all(item.subcategory == 'greetings' for item in materials))

        probe.subcategory = ''
        self.assertEqual(_eligible_materials(probe, 'level1').count(), 18)

    def test_creation_options_include_level_counts(self):
        # 'everyday' fixture, designed so every expected count is unambiguous:
        # 8 level1 items with no subcategory, 2 level3 items under 'colors',
        # and 1 'all'-level item with no subcategory (counts toward all three
        # level buckets at category level, but toward no subcategory).
        category = VocabularyCategory.objects.create(category_name='everyday')
        for i in range(8):
            _vocabulary(category, f'base-{i}', level='level1')
        for i in range(2):
            _vocabulary(category, f'color-{i}', subcategory='colors', level='level3')
        _vocabulary(category, 'any-level', level='all')

        options = _bingo_creation_options()
        entry = next(c for c in options['vocabulary'] if c['name'] == 'everyday')
        self.assertEqual(entry['id'], category.id)
        self.assertEqual(entry['counts'], {'level1': 9, 'level2': 1, 'level3': 3})
        self.assertEqual(entry['subcategories'], [
            {'name': 'colors', 'counts': {'level1': 0, 'level2': 0, 'level3': 2}},
        ])

        # The setUp 'numbers' category: 9 level1 items, no subcategories.
        numbers = next(c for c in options['vocabulary'] if c['name'] == 'numbers')
        self.assertEqual(numbers['counts'], {'level1': 9, 'level2': 0, 'level3': 0})
        self.assertEqual(numbers['subcategories'], [])

    def test_delete_removes_own_game_but_not_for_non_owner(self):
        self._create_via_view(self.creator)
        game = BingoGame.objects.get(audience='personal')

        self.client.force_login(self.other)
        response = self.client.post(reverse('delete_personal_bingo', args=[game.id]))
        self.assertEqual(response.status_code, 404)
        self.assertTrue(BingoGame.objects.filter(pk=game.pk).exists())

        self.client.force_login(self.creator)
        response = self.client.post(reverse('delete_personal_bingo', args=[game.id]))
        self.assertRedirects(response, reverse('student_bingo_list'))
        self.assertFalse(BingoGame.objects.filter(pk=game.pk).exists())
