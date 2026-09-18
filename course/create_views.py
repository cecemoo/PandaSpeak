from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect, render
from django.views import View

from .forms import GroupCourseForm, PrivateCourseForm
from .views import CourseCreateView


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
    form_class = GroupCourseForm
    creation_mode = "group"
    page_title = "Create Group Class"
