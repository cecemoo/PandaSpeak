from django.contrib import admin
from .school_models import SchoolAccount, SchoolEnrollment


@admin.register(SchoolAccount)
class SchoolAccountAdmin(admin.ModelAdmin):
    list_display = ("name", "contact_email", "annual_price", "is_active")
    search_fields = ("name", "contact_email")


@admin.register(SchoolEnrollment)
class SchoolEnrollmentAdmin(admin.ModelAdmin):
    list_display = ("student", "school", "starts_at", "expires_at", "agreed_price", "revoked_at")
    search_fields = ("student__email", "school__name", "payment_reference")
    list_filter = ("school", "revoked_at")
    raw_id_fields = ("student",)
    autocomplete_fields = ("school",)
    readonly_fields = ("created_at",)

    def save_model(self, request, obj, form, change):
        if not change and obj.agreed_price is None:
            obj.agreed_price = obj.school.annual_price
        obj.full_clean()
        super().save_model(request, obj, form, change)
