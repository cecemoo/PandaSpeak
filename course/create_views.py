from django import forms
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect, render
from django.views import View

from .forms import CourseForm, PrivateCourseForm
from .views import CourseCreateView


class DedicatedGroupCourseForm(CourseForm):
    """Group-only form: session type is fixed to group and is not shown to the teacher."""
    def __init__(self, *args, **kwargs):
        initial = kwargs.setdefault('initial', {})
        initial.setdefault('session_type', 'group')
        super().__init__(*args, **kwargs)
        self.fields['session_type'].initial = 'group'
        self.fields['session_type'].widget = forms.HiddenInput()
        self.fields['max_students'].label = 'Maximum group size'
        self.fields['price'].label = 'Price per student'

    def clean(self):
        cleaned = super().clean()
        cleaned['session_type'] = 'group'
        max_students = cleaned.get('max_students') or 1
        if max_students < 2:
            self.add_error('max_students', 'A group class must allow at least 2 students.')
        cleaned['initial_capacity'] = max_students
        return cleaned

    def save(self, commit=True):
        obj = super().save(commit=False)
        obj.session_type = 'group'
        obj.max_students = self.cleaned_data.get('max_students') or 2
        if commit:
            obj.save()
        return obj


class _DedicatedCourseCreateView(LoginRequiredMixin, View):
    template_name = "course/course_form.html"
    form_class = None
    creation_mode = None
    page_title = None

    def get(self, request, *args, **kwargs):
        form = self.form_class()
        return render(request, self.template_name, {
            "form": form,
            "creation_mode": self.creation_mode,
            "page_title": self.page_title,
        })

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST, request.FILES)
        if form.is_valid():
            course = form.save(commit=False)
            course.teacher = request.user
            course.save()
            capacity = form.cleaned_data.get("initial_capacity") or course.max_students
            CourseCreateView().generate_timeslots_for_course(course=course, capacity=capacity)
            if request.user.is_staff:
                return redirect("lessons")
            return redirect("teacher_dashboard")
        return render(request, self.template_name, {
            "form": form,
            "creation_mode": self.creation_mode,
            "page_title": self.page_title,
        })


class PrivateCourseCreateView(_DedicatedCourseCreateView):
    form_class = PrivateCourseForm
    creation_mode = "private"
    page_title = "Create Private Tutoring Session"


class GroupCourseCreateView(_DedicatedCourseCreateView):
    form_class = DedicatedGroupCourseForm
    creation_mode = "group"
    page_title = "Create Group Class"
