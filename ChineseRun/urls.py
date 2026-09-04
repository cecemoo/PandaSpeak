
from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from ChineseRun import settings
from django.http import HttpResponse
from django.contrib.sitemaps.views import sitemap
from account.sitemaps import StaticViewSitemap


sitemaps = {
    "static": StaticViewSitemap,
}

urlpatterns = [
    path(
        'robots.txt',
        lambda request: HttpResponse(
            "User-agent: *\n"
            "Allow: /\n"
            "Sitemap: https://pandaspeak.org/sitemap.xml\n",
            content_type="text/plain"
            )
        ),
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap'),
    path('admin/', admin.site.urls),
    path('', include('account.urls')),
    path('student/', include('student.urls')),
    path('teacher/', include('teacher.urls')),
    path('subscription/', include('subscription.urls')),
    path('course/', include('course.urls')),


    
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
