from django.contrib import admin

from .models import (
    CulturalInsight, CulturalInsightUnlock, LanguageTest,
    StudentSpeakingAnswer, StudentTestSubmission, StudentListeningAnswer,
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
admin.site.register(StudentSpeakingAnswer)


class StudentListeningAnswerInline(admin.TabularInline):
    model = StudentListeningAnswer
    extra = 0
    can_delete = False
    readonly_fields = ('question', 'answer', 'is_correct', 'score')
    fields = readonly_fields
    show_change_link = False


class StudentSpeakingAnswerInline(admin.TabularInline):
    model = StudentSpeakingAnswer
    extra = 0
    can_delete = False
    readonly_fields = ('question', 'audio_file', 'score', 'teacher_feedback', 'submitted_at')
    fields = readonly_fields
    show_change_link = False


@admin.register(StudentTestSubmission)
class StudentTestSubmissionAdmin(admin.ModelAdmin):
    list_display = ('student', 'test', 'submitted_at', 'listening_score',
                    'speaking_score', 'total_score', 'grading_status')
    list_filter = ('is_graded', 'test__test_type', 'submitted_at')
    search_fields = ('student__email', 'test__title')
    readonly_fields = ('student', 'test', 'submitted_at', 'listening_score',
                       'speaking_score', 'total_score', 'is_graded')
    inlines = (StudentListeningAnswerInline, StudentSpeakingAnswerInline)
    ordering = ('-submitted_at',)

    @admin.display(description='Status')
    def grading_status(self, obj):
        if obj.is_graded:
            return 'Graded'
        if obj.speaking_answers.filter(score__isnull=True).exists():
            return 'Waiting for speaking grade'
        return 'Completed'
