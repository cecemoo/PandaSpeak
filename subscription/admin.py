from django.contrib import admin
from .models import StudentActivity, Subscription, TutoringPayment, SubscriptionConsentEvent


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

from django.urls import path
from django.shortcuts import redirect
from django.utils import timezone
from django.contrib import messages
from account.models import CustomUser
from .models import SchoolSubscriptionBatch, SchoolSubscriptionEnrollment

@admin.register(SchoolSubscriptionBatch)
class SchoolSubscriptionBatchAdmin(admin.ModelAdmin):
    list_display = ("school_name", "payment_method", "amount_received", "unit_price", "payment_received_at")
    readonly_fields = ("payment_received_at", "created_by", "created_at")
    def get_readonly_fields(self, request, obj=None):
        fields = list(super().get_readonly_fields(request, obj))
        if obj and obj.payment_received_at:
            fields.extend(["amount_received", "unit_price", "payment_method", "payment_reference", "school_name"])
        return fields
    change_form_template = "admin/subscription/schoolsubscriptionbatch/change_form.html"

    def save_model(self, request, obj, form, change):
        if not change:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)

    def get_urls(self):
        return [
            path("<int:batch_id>/confirm-payment/", self.admin_site.admin_view(self.confirm_payment), name="school_batch_confirm_payment"),
            path("<int:batch_id>/enroll/", self.admin_site.admin_view(self.enroll_student), name="school_batch_enroll"),
        ] + super().get_urls()

    def confirm_payment(self, request, batch_id):
        if request.method == "POST":
            batch = SchoolSubscriptionBatch.objects.get(pk=batch_id)
            if not batch.payment_received_at:
                batch.payment_received_at = timezone.now()
                batch.save(update_fields=["payment_received_at"])
        return redirect("admin:subscription_schoolsubscriptionbatch_change", batch_id)

    def enroll_student(self, request, batch_id):
        if request.method == "POST":
            batch = SchoolSubscriptionBatch.objects.get(pk=batch_id)
            try:
                student = CustomUser.objects.get(email__iexact=request.POST.get("email", "").strip())
                batch.activate_student(student)
                self.message_user(request, "Student enrolled successfully.", messages.SUCCESS)
            except (CustomUser.DoesNotExist, ValueError) as exc:
                self.message_user(request, str(exc), messages.ERROR)
        return redirect("admin:subscription_schoolsubscriptionbatch_change", batch_id)

@admin.register(SchoolSubscriptionEnrollment)
class SchoolSubscriptionEnrollmentAdmin(admin.ModelAdmin):
    list_display = ("batch", "student", "access_until")
    readonly_fields = ("batch", "student", "access_until", "created_at")
    def has_add_permission(self, request):
        return False
