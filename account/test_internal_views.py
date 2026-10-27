from unittest.mock import patch

from django.test import TestCase, override_settings
from django.urls import reverse


class LeadFollowupTriggerTests(TestCase):
    def url(self):
        return reverse("lead_followups_trigger")

    def test_get_is_not_allowed(self):
        response = self.client.get(self.url())
        self.assertEqual(response.status_code, 405)

    @override_settings(LEAD_FOLLOWUP_TOKEN="")
    def test_unconfigured_token_returns_503(self):
        response = self.client.post(self.url())
        self.assertEqual(response.status_code, 503)
        self.assertFalse(response.json()["ok"])

    @override_settings(LEAD_FOLLOWUP_TOKEN="test-token-123")
    def test_missing_or_wrong_token_returns_401_and_does_not_run(self):
        with patch("account.internal_views.call_command") as run:
            self.assertEqual(self.client.post(self.url()).status_code, 401)
            response = self.client.post(
                self.url(), HTTP_AUTHORIZATION="Bearer wrong-token"
            )
            self.assertEqual(response.status_code, 401)
            run.assert_not_called()

    @override_settings(LEAD_FOLLOWUP_TOKEN="test-token-123")
    def test_correct_token_runs_command_and_reports_output(self):
        with patch("account.internal_views.call_command") as run:
            def fake_command(name, stdout=None):
                stdout.write("sent 3 lead follow-up emails")

            run.side_effect = fake_command
            response = self.client.post(
                self.url(), HTTP_AUTHORIZATION="Bearer test-token-123"
            )
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertTrue(payload["ok"])
        self.assertIn("sent 3", payload["output"])
        run.assert_called_once()
        self.assertEqual(run.call_args.args[0], "send_lead_followups")
