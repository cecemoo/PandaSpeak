from django.shortcuts import render
import stripe
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.urls import reverse
from django.views.generic import ListView, DetailView, CreateView, TemplateView
import json
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .models import Course, TimeSlot, Booking
from .forms import CourseForm, GenerateMoreTimeSlotsForm, TimeSlotForm, TimeSlotFormSet
from django.contrib import messages
from django.views import View
from datetime import datetime, timedelta, time
import ast
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError
from django.core.mail import send_mail
from django.db import transaction
from django.db.models import Count, F, Q
from django.views.generic import TemplateView

stripe.api_key = settings.STRIPE_SECRET_KEY 


def get_valid_timezone(timezone_name):

    try:
        return ZoneInfo(timezone_name)
    except (ZoneInfoNotFoundError, TypeError, ValueError):
        return ZoneInfo(settings.TIME_ZONE)


def get_student_timezone(request):
    
    timezone_name = request.session.get("student_timezone")

    if not timezone_name:
        timezone_name = timezone.get_current_timezone_name()

    return timezone_name, get_valid_timezone(timezone_name)


def get_teacher_timezone(course):
    timezone_name = course.teacher_timezone

    if not timezone_name:
        timezone_name = settings.TIME_ZONE

    return timezone_name, get_valid_timezone(timezone_name)


def format_class_time(start_time, end_time, target_timezone):
    local_start = timezone.localtime(
        start_time,
        target_timezone,
    )

    local_end = timezone.localtime(
        end_time,
        target_timezone,
    )

    if local_start.date() == local_end.date():
        return (
            f"{local_start.strftime('%Y-%m-%d %I:%M %p')} – "
            f"{local_end.strftime('%I:%M %p')}"
        )

    return (
        f"{local_start.strftime('%Y-%m-%d %I:%M %p')} – "
        f"{local_end.strftime('%Y-%m-%d %I:%M %p')}"
    )





class CourseListView(ListView):
    model = Course
    template_name = 'course/course_list.html'
    context_object_name = 'courses'
    paginate_by = 12
    ordering = ['-created_at']


class MyCourseListView(LoginRequiredMixin, ListView):
    model = Course
    template_name = 'course/my_course_list.html'
    context_object_name = 'courses'
    paginate_by = 12
    def get_queryset(self):
        return Course.objects.filter(teacher=self.request.user)


class CourseDetailView(DetailView):
    model = Course
    template_name = 'course/course_detail.html'
    context_object_name = 'course'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        course = self.get_object()
        context['available_slots'] = self.object.time_slots.filter(
            start_time__gte=timezone.now()
        ).order_by('start_time')
        return context


class CourseCreateView(LoginRequiredMixin, View):

    template_name = "course/course_form.html"

    def get(self, request, *args, **kwargs):

        form = CourseForm()

        return render(

            request,

            self.template_name,

            {"form": form},

        )

    def post(self, request, *args, **kwargs):

        form = CourseForm(request.POST, request.FILES)

        if form.is_valid():

            course = form.save(commit=False)

            course.teacher = request.user

            course.save()

            initial_capacity = form.cleaned_data.get(

                "initial_capacity",

                1,

            )

            self.generate_timeslots_for_course(

                course=course,

                capacity=initial_capacity,

            )

            if request.user.is_staff:

                return redirect("lessons")

            return redirect("teacher_dashboard")

        return render(

            request,

            self.template_name,

            {"form": form},

        )

    def generate_timeslots_for_course(

        self,

        course,

        capacity=1,

        start_date=None,

        end_date=None,

        available_days=None,

        daily_start_time=None,

        daily_end_time=None,

    ):

        start_date = start_date or course.start_date

        end_date = end_date or course.end_date

        daily_start_time = (

            daily_start_time or course.daily_start_time

        )

        daily_end_time = (

            daily_end_time or course.daily_end_time

        )

        if not start_date or not end_date:

            return

        if not daily_start_time or not daily_end_time:

            return

        if available_days is None:

            raw = (course.available_days or "").strip()

            parts = []

            try:

                if raw.startswith("["):

                    data = ast.literal_eval(raw)

                    if isinstance(data, (list, tuple)):

                        parts = [str(item) for item in data]

                    else:

                        parts = [str(data)]

                else:

                    parts = [

                        part.strip()

                        for part in raw.split(",")

                        if part.strip()

                    ]

            except (ValueError, SyntaxError):

                cleaned = (

                    raw.replace("[", "")

                    .replace("]", "")

                    .replace('"', "")

                    .replace("'", "")

                )

                parts = [

                    part.strip()

                    for part in cleaned.split(",")

                    if part.strip()

                ]

            allowed_days = [

                int(day)

                for day in parts

                if str(day).isdigit()

            ]

        else:

            allowed_days = [

                int(day)

                for day in available_days

            ]

        if not allowed_days:

            return

        try:

            teacher_tz = ZoneInfo(

                course.teacher_timezone

            )

        except (

            ZoneInfoNotFoundError,

            TypeError,

            AttributeError,

        ):

            teacher_tz = ZoneInfo(settings.TIME_ZONE)

        duration = timedelta(

            minutes=course.duration_minutes or 60

        )

        current_day = start_date

        while current_day <= end_date:

            if current_day.weekday() in allowed_days:

                naive_day_start = datetime.combine(

                    current_day,

                    daily_start_time,

                )

                naive_day_end = datetime.combine(

                    current_day,

                    daily_end_time,

                )

                day_start = timezone.make_aware(

                    naive_day_start,

                    teacher_tz,

                )

                day_end = timezone.make_aware(

                    naive_day_end,

                    teacher_tz,

                )

                slot_start = day_start

                while slot_start + duration <= day_end:

                    TimeSlot.objects.update_or_create(

                        course=course,

                        start_time=slot_start,

                        defaults={

                            "end_time": slot_start + duration,

                            "capacity": capacity,

                        },

                    )

                    slot_start += duration

            current_day += timedelta(days=1)



                



class WeeklyScheduleView(LoginRequiredMixin, TemplateView):
    template_name = "course/weekly_schedule.html"
    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        course = get_object_or_404(
            Course,
            pk=kwargs["pk"],
        )

        ctx["course"] = course
        current_tz = timezone.get_current_timezone()
        start_str = self.request.GET.get("start")

        if start_str:
            try:
                week_start = datetime.strptime(
                    start_str,
                    "%Y-%m-%d",
                ).date()
            except ValueError:
                today = timezone.localdate()
                week_start = today - timedelta(
                    days=today.weekday()
                )
        else:
            today = timezone.localdate()
            week_start = today - timedelta(
                days=today.weekday()
            )

        week_end = week_start + timedelta(days=7)
        # Create the beginning and end of the student's local week
        local_week_start = timezone.make_aware(
            datetime.combine(week_start, time.min),
            current_tz,

        )
        local_week_end = timezone.make_aware(
            datetime.combine(week_end, time.min),
            current_tz,
        )
        now = timezone.now()
        timeslots = (
            course.time_slots
            .filter(
                start_time__gte=max(now, local_week_start),
                start_time__lt=local_week_end,
            )
            .select_related("course")
            .prefetch_related("bookings")
            .order_by("start_time")
        )

        slot_map = {}

        for timeslot in timeslots:
            # Convert the stored time to the current student's time zone
            local_start = timezone.localtime(
                timeslot.start_time,
                current_tz,
            )
            local_end = timezone.localtime(
                timeslot.end_time,
                current_tz,
            )
            local_date = local_start.date()
            local_hour = local_start.hour
            if week_start <= local_date < week_end:
                slot_map[(local_date, local_hour)] = {
                    "slot": timeslot,
                    "local_start": local_start,
                    "local_end": local_end,
                }

        days = [
            week_start + timedelta(days=index)
            for index in range(7)
        ]
        hours = []
        for hour in range(24):
            row_cells = []
            for day in days:
                slot_data = slot_map.get((day, hour))
                if slot_data:
                    timeslot = slot_data["slot"]
                    status = (
                        "available"
                        if timeslot.is_available
                        else "full"
                    )
                    row_cells.append({
                        "date": day,
                        "slot": timeslot,
                        "local_start": slot_data["local_start"],
                        "local_end": slot_data["local_end"],
                        "status": status,
                    })
                else:
                    row_cells.append({
                        "date": day,
                        "slot": None,
                        "local_start": None,
                        "local_end": None,
                        "status": "empty",
                    })
            hours.append({
                "hour": hour,
                "cells": row_cells,

            })
        ctx["days"] = days
        ctx["hours"] = hours
        ctx["week_start"] = week_start
        ctx["week_end"] = week_end - timedelta(days=1)
        ctx["prev_start"] = week_start - timedelta(days=7)
        ctx["next_start"] = week_start + timedelta(days=7)
        ctx["student_timezone"] = (
            timezone.get_current_timezone_name()
        )
        ctx["teacher_timezone"] = course.teacher_timezone
        return ctx    




class TimeSlotCreateView(LoginRequiredMixin, CreateView):
    model = TimeSlot
    form_class = TimeSlotForm
    template_name = 'course/timeslot_form.html'

    def dispatch(self, request, *args, **kwargs):
        self.course = get_object_or_404(Course, pk=kwargs['pk'], teacher=request.user)
        return super().dispatch(request, *args, **kwargs)
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['course'] = self.course
        return kwargs

    def form_valid(self, form):
        course = self.course
        form.instance.course = course
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('course:course_detail', args=[self.course.pk])
    
    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['course'] = self.course
        return ctx



@login_required(login_url='my_login')
def generate_more_timeslots(request, pk):
    course = get_object_or_404(Course, pk=pk, teacher=request.user)
    if request.method == 'POST':
        form = GenerateMoreTimeSlotsForm(request.POST)
        if form.is_valid():
            generate_timeslots_for_course(
                course,
                capacity=form.cleaned_data.get('capacity') or 1,
                start_date=form.cleaned_data['start_date'],
                end_date=form.cleaned_data['end_date'],
                available_days=form.cleaned_data['available_days'],
                daily_start_time=form.cleaned_data['daily_start_time'],
                daily_end_time=form.cleaned_data['daily_end_time'],
            )
            return redirect('course:course_detail', pk=course.pk)
    else:
        form = GenerateMoreTimeSlotsForm(initial={
            'start_date': course.start_date,
            'end_date': course.end_date,
            'available_days': course.available_days,
            'daily_start_time': course.daily_start_time,
            'daily_end_time': course.daily_end_time,
        })
    return render(request, 'course/timeslot_form.html', {
        'form': form,
        'course': course,
    })


# for students to view their bookings
@login_required(login_url='my_login')
def my_bookings(request):
    s_bookings = list(
    Booking.objects
    .filter(student=request.user)
    .select_related('timeslot', 'timeslot__course', 'timeslot__course__teacher')
    .order_by('-timeslot__start_time')
    )

    now = timezone.now()

    upcoming_bookings = []
    completed_bookings = []
    canceled_bookings = []

    for b in s_bookings:
       status = b.status.strip().lower()
       b.can_cancel = (
        status == "confirmed" and
        b.timeslot.start_time > now + timedelta(hours=24)
       )
       if status == "confirmed" and b.timeslot.start_time >= now:
           upcoming_bookings.append(b)
       elif status == "confirmed" and b.timeslot.start_time < now:
           completed_bookings.append(b)
       elif status == "canceled":
           canceled_bookings.append(b)

    return render(request, 'course/my_bookings.html', {
        'upcoming_bookings': upcoming_bookings,
        'completed_bookings': completed_bookings,
        'canceled_bookings': canceled_bookings,
        })


@require_POST
def set_student_timezone(request):
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse(
            {"success": False, "error": "Invalid JSON."},
            status=400
        )
    timezone_name = data.get("timezone")
    if not timezone_name:
        return JsonResponse(
            {"success": False, "error": "Missing timezone."},
            status=400
        )
    try:
        ZoneInfo(timezone_name)
    except ZoneInfoNotFoundError:
        return JsonResponse(
            {"success": False, "error": "Invalid timezone."},
            status=400
        )
    request.session["student_timezone"] = timezone_name
    return JsonResponse({"success": True, "timezone": timezone_name})





# for teachers to view bookings for their courses
@login_required(login_url='my_login')
def teacher_bookings(request):
    t_bookings = (Booking.objects.filter(timeslot__course__teacher=request.user).select_related('timeslot__course', 'timeslot', 'student').order_by('-created_at'))
    now = timezone.now()
    for b in t_bookings:
        b.can_cancel = (b.status.lower() == "confirmed" and b.timeslot.start_time > now + timedelta(hours=24))
    return render(request, 'course/teacher_bookings.html', {
        'bookings': t_bookings,
    })



@login_required(login_url='my_login')
def add_to_cart(request, pk):
    slot = get_object_or_404(TimeSlot, pk=pk)
    if not slot.is_available:
        messages.error(request, "This time slot is no longer available.")
        return redirect('course:weekly_schedule', pk=slot.course.pk)
    cart = request.session.get('cart', [])
    if pk not in cart:
        cart.append(pk)
        request.session['cart'] = cart
        request.session.modified = True
        messages.success(request, "Time slot added to cart.")
    else:
        messages.info(request, "Time slot is already in your cart.")
    if request.user.is_staff or request.user == slot.course.teacher:
        messages.error(request, "Teachers/Managers cannot book class slots.")
        return redirect('course:weekly_schedule', pk=slot.course.pk)
    return redirect('course:view_cart')



@login_required(login_url='my_login')
def view_cart(request):
    cart = request.session.get('cart', [])
    slots = TimeSlot.objects.filter(pk__in=cart).select_related('course')
    total_amount = sum(slot.course.price for slot in slots)
    context = {
        'slots': slots,
        'total_amount': total_amount,
    }
    return render(request, 'course/cart.html', context)



@login_required(login_url='my_login')
def remove_from_cart(request, pk):
    cart = request.session.get('cart', [])
    cart = [int(x) for x in cart ]
    if pk in cart:
        cart.remove(pk)
        request.session['cart'] = cart
        request.session.modified = True
        messages.success(request, "Time slot removed from cart.")
    else:
        messages.info(request, "Time slot was not in your cart.")
    return redirect('course:view_cart')



@login_required(login_url='my_login')
def cart_checkout(request):
    cart = request.session.get("cart", [])
    if request.method != "POST":
        return redirect("course:view_cart")

    if not cart:
        messages.error(request, "Your cart is empty.")
        return redirect("course:view_cart")
    # Make sure every cart value is a TimeSlot primary key.
    timeslot_ids = [str(item) for item in cart if item]
    slots = list(
        TimeSlot.objects
        .filter(pk__in=timeslot_ids)
        .select_related("course", "course__teacher")
    )
    if not slots:
        messages.error(request, "No valid classes were found in your cart.")
        return redirect("course:view_cart")
    # Check whether some cart items no longer exist.
    found_ids = {str(slot.pk) for slot in slots}
    missing_ids = [
        timeslot_id
        for timeslot_id in timeslot_ids
        if timeslot_id not in found_ids
    ]
    if missing_ids:
        logger.warning(
            "The following cart TimeSlot IDs were not found: %s",
            missing_ids,
        )
    student_timezone_name, student_tz = get_student_timezone(request)
    line_items = []

    for slot in slots:
        student_time_text = format_class_time(
            slot.start_time, slot.end_time, student_tz,
        )
        line_items.append(
            {
                "price_data": {
                    "currency": "usd",
                    "unit_amount": int(slot.course.price * 100),
                    "product_data": {
                        "name": (
                            f"{slot.course.title} - "
                            f"{student_time_text}"
                        ),
                    },
                },
                "quantity": 1,
            }
        )
    domain = request.build_absolute_uri("/").rstrip("/")
    try:
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            mode="payment",
            customer_email=request.user.email or None,
            line_items=line_items,
            metadata={
                "timeslot_ids": ",".join(
                    str(slot.pk) for slot in slots
                ),
                "user_id": str(request.user.pk),
            },
            success_url=(
                domain
                + reverse("course:cart_payment_success")
                + "?session_id={CHECKOUT_SESSION_ID}"
            ),
            cancel_url=(
                domain
                + reverse("course:cart_payment_cancel")
            ),
        )
    except stripe.error.StripeError:
        logger.exception(
            "Stripe Checkout Session creation failed for user %s",
            request.user.pk,
        )
        messages.error(
            request,
            "We could not start the payment. Please try again.",
        )
        return redirect("course:view_cart")
    # Do not clear the cart here.
    # Clear it only after the booking has been saved successfully.
    return redirect(checkout_session.url, permanent=False)



import logging
logger = logging.getLogger(__name__)

@login_required(login_url='my_login')
def cart_payment_success(request):
    session_id = request.GET.get("session_id")
    if not session_id:
        messages.error(request, "Missing payment session.")
        return redirect("course:course_list")
    try:
        stripe_session = stripe.checkout.Session.retrieve(session_id)
    except stripe.error.StripeError:
        logger.exception(
            "Could not retrieve Stripe session %s",
            session_id,
        )
        messages.error(
            request,
            "We could not verify your payment.",
        )
        return redirect("course:course_list")
    # Do not save a booking unless Stripe confirms payment.
    if stripe_session.payment_status != "paid":
        logger.warning(
            "Stripe session %s is not paid. Payment status: %s",
            session_id,
            stripe_session.payment_status,
        )
        messages.error(
            request,
            "Your payment has not been confirmed.",

        )
        return redirect("course:view_cart")
    metadata = stripe_session.metadata or {}
    try:
        stripe_user_id = str(metadata["user_id"]).strip()
    except (KeyError, TypeError, AttributeError):
        stripe_user_id = ""
    current_user_id = str(request.user.pk)
    if stripe_user_id != current_user_id:
        logger.error(
            "Stripe session user mismatch. Session user=%s, "
            "logged-in user=%s, session=%s",
            stripe_user_id,
            current_user_id,
            session_id,
        )
        messages.error(
            request,
            "This payment session does not belong to your account.",
        )
        return redirect("course:course_list")
    try:
        timeslot_value = str(metadata["timeslot_ids"]).strip()
    except (KeyError, TypeError):
        timeslot_value = ""
    if not timeslot_value:
        logger.error(
            "Stripe session %s has no timeslot_ids metadata. "
            "Metadata: %s",
            session_id,
            dict(metadata),
        )
        messages.error(
            request,
            "Payment was successful, but no class time slots were found. "
            "Please contact PandaSpeak Support.",
        )
        return redirect("course:course_list")
    timeslot_ids = [
        value.strip()
        for value in timeslot_value.split(",")
        if value.strip()
    ]
    payment_intent_id = str(
        stripe_session.payment_intent or ""
    )
    processed_bookings = []
    try:
        with transaction.atomic():
            slots = list(
                TimeSlot.objects
                .select_for_update()
                .filter(pk__in=timeslot_ids)
                .select_related("course", "course__teacher")
            )
            slot_map = {
                str(slot.pk): slot
                for slot in slots
            }
            missing_ids = [
                timeslot_id
                for timeslot_id in timeslot_ids
                if timeslot_id not in slot_map
            ]
            if missing_ids:
                logger.error(
                    "Paid Stripe session %s contains missing "
                    "TimeSlot IDs: %s",
                    session_id,
                    missing_ids,
                )
            for timeslot_id in timeslot_ids:
                slot = slot_map.get(timeslot_id)
                if slot is None:
                    continue
                booking, created = Booking.objects.get_or_create(
                    student=request.user,
                    timeslot=slot,
                    defaults={
                        "status": "confirmed",
                        "stripe_payment_intent_id": payment_intent_id,
                        "stripe_session_id": session_id,
                        "paid_at": timezone.now(),
                        "canceled_at": None,
                        "is_refunded": False,
                    },
                )
                # Also restore/update an existing booking.
                if not created:
                    booking.status = "confirmed"
                    booking.stripe_payment_intent_id = payment_intent_id
                    booking.stripe_session_id = session_id
                    booking.paid_at = timezone.now()
                    booking.canceled_at = None
                    booking.is_refunded = False
                    booking.save(
                        update_fields=[
                            "status",
                            "stripe_payment_intent_id",
                            "stripe_session_id",
                            "paid_at",
                            "canceled_at",
                            "is_refunded",
                        ]
                    )
                processed_bookings.append(booking)
            if not processed_bookings:
                raise ValueError(
                    "No bookings could be created from the "
                    f"TimeSlot IDs: {timeslot_ids}"
                )
    except Exception:
        logger.exception(
            "Booking creation failed after successful payment. "
            "Stripe session=%s, user=%s, timeslots=%s",
            session_id,
            request.user.pk,
            timeslot_ids,
        )
        messages.error(
            request,
            "Your payment was successful, but the booking could not "
            "be saved. Please contact PandaSpeak Support.",
        )
        return redirect("course:course_list")

    # Clear the cart only after the transaction finishes successfully.
    request.session["cart"] = []
    request.session.modified = True

    for booking in processed_bookings:
        slot = booking.timeslot
        course = slot.course
        teacher = course.teacher

        if not teacher.email:
            continue
        teacher_timezone_name, teacher_tz = get_teacher_timezone(course)
        teacher_time_text = format_class_time(
            slot.start_time, slot.end_time, teacher_tz
        )
        try:
            send_mail(
                "New Class Booking Confirmed",
                (
                    f"Dear {teacher.get_full_name()},\n\n"
                    "A new booking has been confirmed for your course "
                    f"'{booking.timeslot.course.title}'.\n\n"
                    f"Student: {request.user.get_full_name()}\n"
                    f"Time: {teacher_time_text}\n"
                    f"Time Zone: {teacher_timezone_name}\n"
                    f"Student Contact Email: {request.user.email}\n\n"
                    "Please contact the student within 24 hours to "
                    "proceed with the class arrangements.\n\n"
                    "Best regards,\n"
                    "PandaSpeak Support Team"
                ),
                settings.DEFAULT_FROM_EMAIL,
                [teacher.email],
                fail_silently=False,
            )
        except Exception:
            logger.exception(
                "Teacher confirmation email failed. Booking ID=%s",
                booking.pk,
            )
    student_timezone_name, student_tz = get_student_timezone(request)
    lines = []

    for booking in processed_bookings:
        slot = booking.timeslot
        teacher = slot.course.teacher
        student_time_text = format_class_time(
            slot.start_time, slot.end_time, student_tz
        )
        lines.append(
            f"Course: {slot.course.title}\n"
            f"Time: {student_time_text}\n"
            f"Time Zone: {student_timezone_name}\n"
            f"Instructor:{teacher.get_full_name()}\n"
        )

    if request.user.email:
        try:
            send_mail(
                "Your Class Booking Confirmation",
                (
                    f"Dear {request.user.get_full_name()},\n\n"
                    "Your payment was successful and the following "
                    "classes have been booked:\n\n"
                    f"{chr(10).join(lines)}\n"
                    "The teacher will contact you shortly to proceed "
                    "with the class arrangements.\n\n"
                    "If the teacher does not contact you within "
                    "24 hours, please contact us so we can assist you.\n\n"
                    "Best regards,\n"
                    "PandaSpeak Support Team"
                ),
                settings.DEFAULT_FROM_EMAIL,
                [request.user.email],
                fail_silently=False,
            )
        except Exception:
            logger.exception(
                "Student confirmation email failed. User ID=%s, "
                "Stripe session=%s",
                request.user.pk,
                session_id,
            )
    messages.success(
        request,
        "Payment successful. Your classes have been booked!",
    )
    return redirect("course:course_list")



# cancel a booking
@login_required(login_url='my_login')
def cancel_booking(request, pk):
    booking = get_object_or_404(Booking, pk=pk)
    is_student = booking.student_id == request.user.id
    is_teacher = booking.timeslot.course.teacher_id == request.user.id
    if not (is_student or is_teacher):
        messages.error(request, "You do not have permission to cancel this booking.")
        return redirect('course:my_bookings')
    
    # prevent cancel too close to start time
    if booking.timeslot.start_time <= timezone.now() + timezone.timedelta(hours=24):
        messages.error(request, "Cannot cancel booking less than 24 hours before start time.")
        return redirect('course:my_bookings')

    slot = booking.timeslot
    student = booking.student
    teacher = slot.course.teacher
    student_timezone_name, student_tz = get_student_timezone(request)
    teacher_timezone_name, teacher_tz = get_teacher_timezone(slot.course)
    student_time_text = format_class_time(
        slot.start_time, slot.end_time, student_tz
    )
    teacher_time_text = format_class_time(
        slot.start_time, slot.end_time, teacher_tz
    )
    
    try:
        if booking.stripe_payment_intent_id and not booking.is_refunded:
            stripe.Refund.create(
                payment_intent=booking.stripe_payment_intent_id

            )
            booking.is_refunded = True
            booking.save()
    except stripe.error.StripeError as e:
        messages.error(request, f"Refund failed: {str(e)}. Please contact support.")
        return redirect('course:my_bookings')
    
    booking.cancel()
    if student.email:
        send_mail(
            "Your Class Booking Has Been Cancelled",
            (
                f"Dear {student.first_name} {student.last_name},\n\n"
                f"Your booking for the class '{slot.course.title}' scheduled on {student_time_text} ({student_timezone_name}) has been successfully cancelled.\n\n"
                f"A refund has been initiated and should be processed within 5-10 business days depending on your bank.\n\n"
                f"In any event if you do not see the refund in your account within 10 business days, please contact us immediately so we can assist you.\n\n"
                f"Best regards, \n"
                f"PandaSpeak Support Team"
            ),
            settings.DEFAULT_FROM_EMAIL,
            [student.email],
            fail_silently=False,
        )
    if teacher.email:
        send_mail(
            "A Class Booking Has Been Cancelled",
            (
                f"Dear {teacher.get_full_name()},\n\n"
                f"The booking for your class '{slot.course.title}' scheduled on {teacher_time_text} ({teacher_timezone_name}) has been cancelled by the student.\n\n"
                f"Best regards, \n"
                f"PandaSpeak Support Team"
            ),
            settings.DEFAULT_FROM_EMAIL,
            [teacher.email],
            fail_silently=False,
        )
    messages.success(request, "Booking has been cancelled.")
    return redirect('course:my_bookings' if is_student else 'course:teacher_bookings')





@login_required(login_url='my_login')
def cart_payment_cancel(request):
    messages.info(request, "Payment was cancelled.")
    return render(request, 'course/payment_cancel.html')




