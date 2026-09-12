from django.contrib import admin
from .models import (
    Announcement,
    AnnouncementDelivery,
    CustomUser,
    PlacementQuestion,
    PrivacyPolicy,
    TermsOfService,
)


@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    list_display = ('subject', 'created_by', 'created_at', 'queued_at', 'delivery_count')
    list_filter = ('created_at', 'queued_at')
    search_fields = ('subject', 'body', 'created_by__email')
    readonly_fields = ('created_at', 'queued_at')
    ordering = ('-created_at',)

    @admin.display(description='Deliveries')
    def delivery_count(self, obj):
        return obj.deliveries.count()


@admin.register(AnnouncementDelivery)
class AnnouncementDeliveryAdmin(admin.ModelAdmin):
    list_display = ('announcement', 'user', 'status')
    list_filter = ('status',)
    search_fields = ('announcement__subject', 'user__email')
    autocomplete_fields = ('announcement', 'user')


admin.site.register(CustomUser)
admin.site.register(TermsOfService)
admin.site.register(PrivacyPolicy)
admin.site.register(PlacementQuestion)
