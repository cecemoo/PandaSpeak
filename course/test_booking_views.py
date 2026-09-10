from datetime import timedelta

from django import forms
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db import transaction
from django.shortcuts import redirect, render
from django.utils import timezone

from .models import Booking, Course, TimeSlot


User = get_user_model()


class UserChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        name = obj.get_full_name() or obj.email
        return f"{name} — {obj.email}"


class CourseChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        teacher = obj.teacher.get_full_name() or obj.teacher.email
        return f"{obj.title} — Teacher: {teacher}"


class TestTutoringBookingForm(forms.Form):
    student = UserChoiceField(queryset=User.objects.none(), label="Test student")
    course = CourseChoiceField(queryset=Course.objects.none(), label="Course / teacher")
    start_time = forms.DateTimeField(
        label="Test session start",
        widget=forms.DateTimeInput(attrs={"type": "datetime-local"}),
        input_formats=["%Y-%m-%dT%H:%M"],
        help_text="Choose a time near now. The room opens 15 minutes before the start time.",
    )
    duration_minutes = forms.IntegerField(
        min_value=5,
        max_value=120,
        initial=10,
        label="Test slot length (minutes)",
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["student"].queryset = User.objects.filter(
            is_active=True,
            is_teacher=False,
            is_staff=False,
            is_superuser=False,
        ).order_by("first_name", "last_name", "email")
        self.fields["course"].queryset = Course.objects.select_related("teacher").filter(
            teacher__is_active=True,
            teacher__is_teacher=True,
        ).order_by("title")
        if not self.is_bound:
            local_now = timezone.localtime(timezone.now()).replace(second=0, microsecond=0)
            self.initial["start_time"] = local_now.strftime("%Y-%m-%dT%H:%M")


def manager_only(user):
    return user.is_authenticated and user.is_staff


@login_required(login_url="my_login")
@user_passes_test(manager_only, login_url="my_login")
def create_test_tutoring_booking(request):
    form = TestTutoringBookingForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        student = form.cleaned_data["student"]
        course = form.cleaned_data["course"]
        start_time = form.cleaned_data["start_time"]
        duration_minutes = form.cleaned_data["duration_minutes"]
        end_time = start_time + timedelta(minutes=duration_minutes)

        with transaction.atomic():
            slot = TimeSlot.objects.create(
                course=course,
                start_time=start_time,
                end_time=end_time,
                capacity=1,
            )
            booking = Booking.objects.create(
                student=student,
                timeslot=slot,
                status="confirmed",
                paid_at=timezone.now(),
                is_test_booking=True,
                session_status="scheduled",
                payout_status="pending",
            )

        messages.success(
            request,
            (
                f"Test tutoring booking #{booking.pk} created for {student.email} with "
                f"{course.teacher.email}. No Stripe charge or transfer was created. "
                "Sign in as the student and teacher in separate browsers to test the session."
            ),
        )
        return redirect("course:create_test_tutoring_booking")

    return render(
        request,
        "course/create_test_tutoring_booking.html",
        {"form": form},
    )
