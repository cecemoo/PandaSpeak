
from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from ChineseRun import settings



urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('account.urls')),
    path('student/', include('student.urls')),
    path('teacher/', include('teacher.urls')),
    path('subscription/', include('subscription.urls')),


    
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
