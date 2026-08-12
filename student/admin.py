from django.contrib import admin

from .models import LanguageTest, TestQuestion, StudentSpeakingAnswer


admin.site.register(LanguageTest)
admin.site.register(TestQuestion)
admin.site.register(StudentSpeakingAnswer)


