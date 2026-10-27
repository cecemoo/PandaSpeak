from unittest.mock import patch

from django.test import TestCase
from django.urls import reverse

from account.lead_attribution import _classify
from account.models import LeadMagnetSignup


class ClassifyTests(TestCase):
    def test_utm_aliases_win(self):
        self.assertEqual(_classify("", "fb"), "facebook")
        self.assertEqual(_classify("", "Instagram"), "instagram")
        self.assertEqual(_classify("www.google.com", "threads"), "threads")

    def test_host_classification(self):
        self.assertEqual(_classify("l.facebook.com"), "facebook")
        self.assertEqual(_classify("l.instagram.com"), "instagram")
        self.assertEqual(_classify("www.threads.net"), "threads")
        self.assertEqual(_classify("www.google.com"), "google")
        self.assertEqual(_classify("www.bing.com"), "bing")
        self.assertEqual(_classify("pandaspeak.org"), "internal")
        self.assertEqual(_classify("www.reddit.com"), "www.reddit.com")
        self.assertEqual(_classify(""), "direct")


class LeadSignupAttributionTests(TestCase):
    def _signup(self, url_name, email, **get_kwargs):
        with patch("account.views._send_lead_email"):
            self.client.get(reverse(url_name), **get_kwargs)
            return self.client.post(
                reverse(url_name), {"email": email, "consent": "yes"}
            )

    def test_facebook_referrer_recorded(self):
        response = self._signup(
            "free_bopomofo_chart", "fb-visitor@example.com",
            HTTP_REFERER="https://l.facebook.com/l.php?u=example",
        )
        self.assertEqual(response.status_code, 302)
        signup = LeadMagnetSignup.objects.get(email="fb-visitor@example.com")
        self.assertEqual(signup.traffic_source, "facebook")
        self.assertIn("l.facebook.com", signup.referrer)

    def test_instagram_utm_recorded(self):
        self._signup(
            "free_chinese_idioms", "ig-visitor@example.com",
        )
        # second visit pattern: fresh client carrying utm on the GET
        self.client.cookies.clear()
        with patch("account.views._send_lead_email"):
            self.client.get(
                reverse("free_chinese_idioms") + "?utm_source=instagram"
            )
            self.client.post(
                reverse("free_chinese_idioms"),
                {"email": "ig-utm@example.com", "consent": "yes"},
            )
        signup = LeadMagnetSignup.objects.get(email="ig-utm@example.com")
        self.assertEqual(signup.traffic_source, "instagram")

    def test_direct_when_no_referrer(self):
        self._signup("free_bopomofo_chart", "direct-visitor@example.com")
        signup = LeadMagnetSignup.objects.get(email="direct-visitor@example.com")
        self.assertEqual(signup.traffic_source, "direct")
