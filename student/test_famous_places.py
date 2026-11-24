"""Tests for the Famous Spots & Food Map page."""
import os
from decimal import Decimal

from django.conf import settings
from django.test import TestCase
from django.urls import reverse

from account.models import CustomUser
from student.places_data import PHOTO_CREDITS, SPOTS
from subscription.models import Subscription


def _subscriber(email, level='level1'):
    user = CustomUser.objects.create_user(
        email=email, password='<redacted>', first_name='Pat', last_name='Student')
    user.learning_level = level
    user.save()
    Subscription.objects.create(
        user=user, subscription_plan='Base', subscription_cost=Decimal('15.00'), is_active=True)
    return user


class FamousPlacesPageTests(TestCase):
    def setUp(self):
        self.user = _subscriber('traveler@example.com', level='level1')
        self.client.force_login(self.user)

    def test_page_loads_for_level1(self):
        response = self.client.get(reverse('famous_places'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Famous Spots')
        self.assertContains(response, '景點美食地圖')
        self.assertContains(response, 'fp-map')

    def test_page_shows_every_spot(self):
        response = self.client.get(reverse('famous_places'))
        for spot in SPOTS:
            self.assertContains(response, spot['city']['chars'])
            self.assertContains(response, spot['landmark']['chars'])
            self.assertContains(response, spot['food']['chars'])

    def test_dashboard_has_card_for_level1(self):
        response = self.client.get(reverse('student_dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Famous Spots &amp; Food')
        self.assertContains(response, reverse('famous_places'))


class FamousPlacesDataTests(TestCase):
    def test_ten_spots_covering_china_hk_taiwan_macau(self):
        self.assertEqual(len(SPOTS), 10)
        regions = {spot['region'] for spot in SPOTS}
        self.assertIn('Hong Kong', regions)
        self.assertIn('Macau', regions)
        self.assertIn('Taiwan', regions)
        self.assertTrue(any('China' in r for r in regions))

    def test_every_spot_is_complete(self):
        places_dir = os.path.join(settings.BASE_DIR, 'student', 'static', 'student', 'places')
        slugs = set()
        for spot in SPOTS:
            slugs.add(spot['slug'])
            for key in ('photo', 'food_photo'):
                self.assertTrue(os.path.exists(os.path.join(places_dir, spot[key])),
                                f"{spot['slug']} missing {spot[key]}")
                self.assertIn(spot[key], PHOTO_CREDITS)
            self.assertTrue(spot['intro'])
            self.assertGreaterEqual(len(spot['place_vocab']), 3)
            self.assertGreaterEqual(len(spot['food_vocab']), 2)
            for word in spot['place_vocab'] + spot['food_vocab'] + [spot['city'], spot['food']]:
                for field in ('chars', 'bopomofo', 'pinyin', 'english'):
                    self.assertTrue(word[field], f"{spot['slug']} word missing {field}")
            self.assertEqual(len(spot['quiz']), 2)
            for question in spot['quiz']:
                self.assertEqual(len(question['choices']), 4)
                self.assertIn(question['answer'], range(4))
            left, top = spot['pin']
            self.assertTrue(0 <= left <= 100 and 0 <= top <= 100)
        self.assertEqual(len(slugs), len(SPOTS))
