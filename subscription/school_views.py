from datetime import datetime, time
from decimal import Decimal
import stripe
from django.conf import settings
from django import forms
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db import transaction
from django.shortcuts import redirect, render
from django.utils import timezone
from account.models import CustomUser
from .models import Subscription, BlockedPurchaseEmail
from .school_models import SchoolAccount, SchoolEnrollment, SchoolPayment


class SchoolForm(forms.ModelForm):
    class Meta:
        model = SchoolAccount
        fields = ("name", "contact_email", "annual_price", "is_active")


class SchoolPaymentForm(forms.Form):
    school = forms.ModelChoiceField(queryset=SchoolAccount.objects.filter(is_active=True))
    method = forms.ChoiceField(choices=SchoolPayment.METHOD_CHOICES)
    amount = forms.DecimalField(min_value=Decimal("0.01"), max_digits=10, decimal_places=2)
    reference = forms.CharField(max_length=200, required=False)
    received = forms.BooleanField(required=False)

    def clean(self):
        data = super().clean()
        if data.get("method") in ("cash", "wire") and (not data.get("received") or not (data.get("reference") or "").strip()):
            raise forms.ValidationError("Confirm receipt and enter a receipt or wire reference.")
        return data


class EnrollmentForm(forms.Form):
    school = forms.ModelChoiceField(queryset=SchoolAccount.objects.filter(is_active=True))
    student_email = forms.EmailField()
    starts_at = forms.DateField(initial=timezone.localdate, widget=forms.DateInput(attrs={"type": "date"}))
    expires_at = forms.DateField(widget=forms.DateInput(attrs={"type": "date"}))
    payment = forms.ModelChoiceField(queryset=SchoolPayment.objects.none())

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["payment"].queryset = SchoolPayment.objects.filter(received_at__isnull=False, reversed_at__isnull=True)

    def clean(self):
        cleaned = super().clean()
        if cleaned.get("starts_at") and cleaned.get("expires_at") and cleaned["expires_at"] <= cleaned["starts_at"]:
            raise forms.ValidationError("Expiration must be after the start date.")
        if cleaned.get("payment") and cleaned.get("school") and cleaned["payment"].school_id != cleaned["school"].pk:
            raise forms.ValidationError("Payment belongs to another school.")
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
    payment_form = SchoolPaymentForm(prefix="payment")
    if request.method == "POST":
        action = request.POST.get("action")
        if action == "school":
            school_form = SchoolForm(request.POST, prefix="school")
            if school_form.is_valid():
                school_form.save()
                messages.success(request, "School saved.")
                return redirect("manage_school_subscriptions")
        elif action == "payment":
            payment_form = SchoolPaymentForm(request.POST, prefix="payment")
            if payment_form.is_valid():
                data = payment_form.cleaned_data
                if data["method"] == "card":
                    payment = SchoolPayment.objects.create(school=data["school"], method="card", amount=data["amount"])
                    try:
                        session = stripe.checkout.Session.create(
                            api_key=getattr(settings, "STRIPE_SUBSCRIPTION_SECRET_KEY", "") or settings.STRIPE_SECRET_KEY,
                            mode="payment", payment_method_types=["card"],
                            line_items=[{"price_data": {"currency": "usd", "unit_amount": int(data["amount"] * 100),
                                "product_data": {"name": "PandaSpeak school payment"}}, "quantity": 1}],
                            success_url=request.build_absolute_uri("/subscription/manager/schools/"),
                            cancel_url=request.build_absolute_uri("/subscription/manager/schools/"),
                            metadata={"purpose": "pandaspeak_school_payment", "payment_id": str(payment.pk)},
                            idempotency_key=f"school-payment-{payment.pk}",
                        )
                        payment.stripe_session_id = session.id
                        payment.save(update_fields=["stripe_session_id"])
                        return redirect(session.url)
                    except stripe.error.StripeError:
                        payment.delete()
                        messages.error(request, "Stripe checkout unavailable.")
                else:
                    SchoolPayment.objects.create(school=data["school"], method=data["method"],
                        amount=data["amount"], reference=data["reference"].strip(),
                        received_at=timezone.now(), confirmed_by=request.user)
                    messages.success(request, "School payment recorded.")
                    return redirect("manage_school_subscriptions")
        elif action == "verify_payment":
            payment = SchoolPayment.objects.filter(pk=request.POST.get("payment_id"), method="card", received_at__isnull=True).first()
            if payment and payment.stripe_session_id:
                try:
                    session = stripe.checkout.Session.retrieve(payment.stripe_session_id,
                        api_key=getattr(settings, "STRIPE_SUBSCRIPTION_SECRET_KEY", "") or settings.STRIPE_SECRET_KEY)
                    metadata = session.get("metadata") or {}
                    if (session.get("payment_status") == "paid" and session.get("status") == "complete"
                            and metadata.get("purpose") == "pandaspeak_school_payment"
                            and metadata.get("payment_id") == str(payment.pk)
                            and session.get("amount_total") == int(payment.amount * 100)
                            and session.get("currency") == "usd"):
                        payment.received_at = timezone.now()
                        payment.reference = session.get("payment_intent") or session.id
                        payment.save(update_fields=["received_at", "reference"])
                        messages.success(request, "Stripe payment verified.")
                    else:
                        messages.error(request, "Stripe has not confirmed payment.")
                except stripe.error.StripeError:
                    messages.error(request, "Stripe verification unavailable.")
            return redirect("manage_school_subscriptions")
        elif action == "enroll":
            enrollment_form = EnrollmentForm(request.POST, prefix="enrollment")
            if enrollment_form.is_valid():
                data = enrollment_form.cleaned_data
                with transaction.atomic():
                    payment = SchoolPayment.objects.select_for_update().get(pk=data["payment"].pk, received_at__isnull=False, reversed_at__isnull=True)
                    used = sum((item.agreed_price for item in payment.enrollments.all()), Decimal("0.00"))
                    if used + data["school"].annual_price > payment.amount:
                        enrollment_form.add_error("payment", "Insufficient remaining payment balance.")
                    else:
                        SchoolEnrollment.objects.create(
                            school=data["school"], student=data["student"],
                            starts_at=timezone.make_aware(datetime.combine(data["starts_at"], time.min)),
                            expires_at=timezone.make_aware(datetime.combine(data["expires_at"], time.min)),
                            agreed_price=data["school"].annual_price,
                            payment=payment, payment_reference=f"{payment.method}:{payment.reference}",
                        )
                        messages.success(request, "Paid school subscription assigned.")
                        return redirect("manage_school_subscriptions")
        elif action == "revoke":
            record = SchoolEnrollment.objects.filter(pk=request.POST.get("enrollment_id"), revoked_at__isnull=True).first()
            if record:
                record.revoked_at = timezone.now()
                record.save(update_fields=["revoked_at"])
                messages.success(request, "School access revoked.")
            return redirect("manage_school_subscriptions")
    return render(request, "subscription/manage_schools.html", {
        "school_form": school_form, "enrollment_form": enrollment_form, "payment_form": payment_form,
        "payments": SchoolPayment.objects.select_related("school").order_by("-created_at")[:200],
        "schools": SchoolAccount.objects.all().order_by("name"),
        "enrollments": SchoolEnrollment.objects.select_related("school", "student").order_by("-created_at")[:200],
        "now": timezone.now(),
    })
