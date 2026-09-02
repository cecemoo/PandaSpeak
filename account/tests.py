from django.core import mail
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from .models import PlacementQuestion, PlacementTestAttempt


@override_settings(
    EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend',
)
class PlacementTestTests(TestCase):
    def setUp(self):
        self.question = PlacementQuestion.objects.create(
            level='level1',
            prompt='Select the correct answer.',
            choice_a='Correct',
            choice_b='Incorrect',
            choice_c='Incorrect',
            choice_d='Incorrect',
            correct_answer='A',
            order=1,
        )
        self.test_url = reverse('placement_test')
        self.email_url = reverse('email_placement_test_result')

    def take_test(self, client=None, ip='203.0.113.10'):
        client = client or self.client
        return client.post(
            self.test_url,
            {f'question_{self.question.pk}': 'A'},
            REMOTE_ADDR=ip,
        )

    def test_completed_attempt_is_saved_and_same_browser_cannot_retake(self):
        response = self.take_test()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(PlacementTestAttempt.objects.count(), 1)

        response = self.client.get(self.test_url, REMOTE_ADDR='203.0.113.10')
        self.assertContains(response, 'already completed the free placement test')
        self.assertEqual(PlacementTestAttempt.objects.count(), 1)

    def test_same_ip_is_blocked_in_a_different_browser(self):
        self.take_test()
        other_browser = Client()

        response = self.take_test(other_browser)

        self.assertContains(response, 'already completed the free placement test')
        self.assertEqual(PlacementTestAttempt.objects.count(), 1)

    def test_result_can_be_emailed(self):
        self.take_test()

        response = self.client.post(
            self.email_url,
            {'email': 'learner@example.com'},
        )

        self.assertContains(response, 'emailed successfully')
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, ['learner@example.com'])
        self.assertIn('Score: 1 / 1 (100%)', mail.outbox[0].body)
        attempt = PlacementTestAttempt.objects.get()
        self.assertEqual(attempt.result_email, 'learner@example.com')
        self.assertIsNotNone(attempt.emailed_at)

    def test_email_requires_a_valid_address(self):
        self.take_test()

        response = self.client.post(self.email_url, {'email': 'not-an-email'})

        self.assertContains(response, 'Enter a valid email address')
        self.assertEqual(mail.outbox, [])
