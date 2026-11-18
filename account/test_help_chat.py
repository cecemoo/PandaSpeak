import json
import os
from unittest import mock

from django.core.cache import cache
from django.test import Client, TestCase, override_settings


class FakeResponse:
    def raise_for_status(self):
        pass

    def json(self):
        return {'output_text': 'Base subscription is $15/year. [Subscribe here](/subscription/subscribe/)'}


@override_settings(ALLOWED_HOSTS=['*'])
class HelpChatViewTests(TestCase):
    def setUp(self):
        cache.clear()
        self.client = Client(HTTP_HOST='localhost')

    def post(self, payload):
        return self.client.post('/help-chat/', data=json.dumps(payload),
                                content_type='application/json', HTTP_HOST='localhost')

    def test_get_not_allowed(self):
        response = self.client.get('/help-chat/', HTTP_HOST='localhost')
        self.assertEqual(response.status_code, 405)

    def test_empty_message_rejected(self):
        response = self.post({'message': '   '})
        self.assertEqual(response.status_code, 400)

    def test_invalid_json_rejected(self):
        response = self.client.post('/help-chat/', data='not json',
                                    content_type='application/json', HTTP_HOST='localhost')
        self.assertEqual(response.status_code, 400)

    def test_reply_returned(self):
        with mock.patch.dict(os.environ, {'OPENAI_API_KEY': 'test-key'}), \
                mock.patch('account.help_chat_views.requests.post', return_value=FakeResponse()) as mocked:
            response = self.post({'message': 'How much does it cost?',
                                  'history': [{'role': 'user', 'content': 'hi'},
                                              {'role': 'assistant', 'content': 'Hello!'}]})
        self.assertEqual(response.status_code, 200)
        self.assertIn('$15/year', response.json()['reply'])
        payload = mocked.call_args.kwargs['json']
        roles = [item['role'] for item in payload['input']]
        self.assertEqual(roles[0], 'system')
        self.assertEqual(roles[-1], 'user')

    def test_fallback_when_ai_fails(self):
        with mock.patch('account.help_chat_views.requests.post', side_effect=RuntimeError('down')):
            response = self.post({'message': 'hello'})
        self.assertEqual(response.status_code, 200)
        self.assertIn('/register/', response.json()['reply'])

    def test_rate_limit(self):
        with mock.patch.dict(os.environ, {'OPENAI_API_KEY': 'test-key'}), \
                mock.patch('account.help_chat_views.RATE_LIMIT_PER_HOUR', 2), \
                mock.patch('account.help_chat_views.requests.post', return_value=FakeResponse()):
            self.assertIn('reply', self.post({'message': 'one'}).json())
            self.assertIn('reply', self.post({'message': 'two'}).json())
            third = self.post({'message': 'three'}).json()['reply']
        self.assertIn('try again a little later', third)


class HelpWidgetRenderingTests(TestCase):
    def test_bubble_and_panel_on_homepage(self):
        response = Client(HTTP_HOST='localhost').get('/', HTTP_HOST='localhost')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'id="ps-help-bubble"')
        self.assertContains(response, 'Get Help')
        self.assertContains(response, 'id="ps-help-panel"')
