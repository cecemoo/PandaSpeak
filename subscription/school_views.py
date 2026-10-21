from datetime import datetime, time
from django import forms
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db import transaction
from django.shortcuts import redirect, render
from django.utils import timezone
from account.models import CustomUser
from .models import Subscription, BlockedPurchaseEmail
from .school_models import SchoolAccount, SchoolEnrollment


class SchoolForm(forms.ModelForm):
    class Meta:
        model = SchoolAccount
        fields = ("name", "contact_email", "annual_price", "is_active")


class EnrollmentForm(forms.Form):
    school = forms.ModelChoiceField(queryset=SchoolAccount.objects.filter(is_active=True))
    student_email = forms.EmailField()
    starts_at = forms.DateField(initial=timezone.localdate, widget=forms.DateInput(attrs={"type": "date"}))
    expires_at = forms.DateField(widget=forms.DateInput(attrs={"type": "date"}))
    payment_reference = forms.CharField(max_length=200, required=False)

    def clean(self):
        cleaned = super().clean()
        if cleaned.get("starts_at") and cleaned.get("expires_at") and cleaned["expires_at"] <= cleaned["starts_at"]:
            raise forms.ValidationError("Expiration must be after the start date.")
        email = cleaned.get("student_email")
        if email:
            student = CustomUser.objects.filter(email__iexact=email).first()
            if not student or not student.is_active or student.is_staff or student.is_teacher:
                raise forms.ValidationError("An active student account with that email is required.")
            if Subscription.objects.filter(user=student, is_disputed=True).exists() or BlockedPurchaseEmail.objects.filter(email__iexact=email).exists():
                raise forms.ValidationError("This student has a payment restriction.")
            existing = Subscription.objects.filter(user=student).first()
            if existing and existing.is_active and (not existing.access_until or existing.access_until > timezone.now()):
                raise forms.ValidationError("This student already has an active individual subscription.")
            if SchoolEnrollment.objects.filter(
                student=student, revoked_at__isnull=True,
                starts_at__lt=timezone.make_aware(datetime.combine(cleaned["expires_at"], time.min)),
                expires_at__gt=timezone.make_aware(datetime.combine(cleaned["starts_at"], time.min)),
            ).exists():
                raise forms.ValidationError("This student already has a school enrollment overlapping these dates.")
            cleaned["student"] = student
        return cleaned


@login_required
@user_passes_test(lambda user: user.is_staff or user.is_superuser)
def manage_schools(request):
    school_form = SchoolForm(prefix="school")
    enrollment_form = EnrollmentForm(prefix="enrollment")
    if request.method == "POST":
        action = request.POST.get("action")
        if action == "school":
            school_form = SchoolForm(request.POST, prefix="school")
            if school_form.is_valid():
                school_form.save()
                messages.success(request, "School saved.")
                return redirect("manage_school_subscriptions")
        elif action == "enroll":
            enrollment_form = EnrollmentForm(request.POST, prefix="enrollment")
            if enrollment_form.is_valid():
                data = enrollment_form.cleaned_data
                with transaction.atomic():
                    SchoolEnrollment.objects.create(
                        school=data["school"], student=data["student"],
                        starts_at=timezone.make_aware(datetime.combine(data["starts_at"], time.min)),
                        expires_at=timezone.make_aware(datetime.combine(data["expires_at"], time.min)),
                        agreed_price=data["school"].annual_price,
                        payment_reference=data["payment_reference"],
                    )
                messages.success(request, "School subscription assigned.")
                return redirect("manage_school_subscriptions")
        elif action == "revoke":
            record = SchoolEnrollment.objects.filter(pk=request.POST.get("enrollment_id"), revoked_at__isnull=True).first()
            if record:
                record.revoked_at = timezone.now()
                record.save(update_fields=["revoked_at"])
                messages.success(request, "School access revoked.")
            return redirect("manage_school_subscriptions")
    return render(request, "subscription/manage_schools.html", {
        "school_form": school_form, "enrollment_form": enrollment_form,
        "schools": SchoolAccount.objects.all().order_by("name"),
        "enrollments": SchoolEnrollment.objects.select_related("school", "student").order_by("-created_at")[:200],
        "now": timezone.now(),
    })
