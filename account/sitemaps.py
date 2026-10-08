from django.contrib.sitemaps import Sitemap
from django.urls import reverse




class StaticViewSitemap(Sitemap):
    priority = 0.8
    changefreq = "weekly"
    def items(self):
        return [
            "home",
            "about",
            "learn_traditional_chinese_online",
            "bopomofo_for_adults",
            "placement_test",
            "faq",
            "terms",
            "privacy",
        ]
    def location(self, item):
        return reverse(item)

