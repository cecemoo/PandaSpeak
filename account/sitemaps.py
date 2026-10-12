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
            "learn_chinese_idioms",
            "free_bopomofo_chart",
            "free_chinese_idioms",
            "placement_test",
            "faq",
            "terms",
            "privacy",
        ]
    def location(self, item):
        return reverse(item)

