from django.contrib import admin

from .models import (
    CulturalInsight, CulturalInsightUnlock, LanguageTest, TestQuestion,
    StudentSpeakingAnswer,
)


@admin.register(CulturalInsight)
class CulturalInsightAdmin(admin.ModelAdmin):
    list_display = ('title', 'chinese_title', 'level', 'category', 'is_published', 'order', 'updated_at')
    list_filter = ('level', 'category', 'is_published')
    search_fields = ('title', 'chinese_title', 'summary', 'content')
    list_editable = ('is_published', 'order')
    ordering = ('level', 'order', 'title')


@admin.register(CulturalInsightUnlock)
class CulturalInsightUnlockAdmin(admin.ModelAdmin):
    list_display = ('student', 'insight', 'unlocked_at')
    list_filter = ('insight__level', 'insight__category')
    search_fields = ('student__email', 'insight__title', 'insight__chinese_title')
    readonly_fields = ('unlocked_at',)


admin.site.register(LanguageTest)
admin.site.register(TestQuestion)
admin.site.register(StudentSpeakingAnswer)
