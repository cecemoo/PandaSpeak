from django.contrib import admin
from .models import StudentActivity, Subscription, TutoringPayment


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = (
        "user", "subscription_plan", "is_active", "is_cancelled",
        "is_disputed", "dispute_status", "dispute_provider", "disputed_at",
        "checkout_terms_accepted_at", "checkout_terms_version",
    )
    list_filter = ("is_active", "is_cancelled", "is_disputed", "dispute_provider", "dispute_status")
    search_fields = ("user__email", "user__first_name", "user__last_name", "stripe_subscription_id", "paypal_subscription_id", "dispute_external_id")
    readonly_fields = ("disputed_at", "checkout_terms_accepted_at", "checkout_terms_version")


@admin.register(StudentActivity)
class StudentActivityAdmin(admin.ModelAdmin):
    list_display = ("created_at", "user", "activity_type", "method", "view_name", "path", "ip_address", "response_status")
    list_filter = ("activity_type", "method", "response_status", "created_at")
    search_fields = ("user__email", "user__first_name", "user__last_name", "path", "view_name", "ip_address")
    readonly_fields = ("user", "activity_type", "method", "path", "view_name", "ip_address", "user_agent", "response_status", "created_at")
    date_hierarchy = "created_at"


admin.site.register(TutoringPayment)


@admin.register(SubscriptionConsentEvent)
class SubscriptionConsentEventAdmin(admin.ModelAdmin):
    list_display = ("user", "accepted_at", "terms_version", "terms_accepted", "faq_accepted", "payment_provider", "checkout_status")
    list_filter = ("payment_provider", "checkout_status", "terms_version")
    search_fields = ("user__email",)
    readonly_fields = ("user", "accepted_at", "terms_version", "terms_accepted", "faq_accepted", "payment_provider", "checkout_status", "provider_session_id", "ip_address", "user_agent")
    def has_add_permission(self, request):
        return False
    def has_change_permission(self, request, obj=None):
        return False
    def has_delete_permission(self, request, obj=None):
        return False
