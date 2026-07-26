from django.shortcuts import render
import stripe
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.urls import reverse
from django.views.generic import ListView, DetailView, CreateView, TemplateView


from .models import Course, TimeSlot, Booking
from .forms import CourseForm, GenerateMoreTimeSlotsForm, TimeSlotForm, TimeSlotFormSet
from datetime import timedelta
from django.contrib import messages
from django.views import View
from datetime import datetime, timedelta
import ast
from django.core.mail import send_mail
from django.db import transaction
from django.db.models import Count, F, Q


stripe.api_key = settings.STRIPE_SECRET_KEY 



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
        context['available_slots'] = [slot for slot in course.time_slots.all() if slot.is_available]
        return context


class CourseCreateView(LoginRequiredMixin, View):
    template_name = 'course/course_form.html'
    def get(self, request, *args, **kwargs):
        form = CourseForm()
        return render(request, self.template_name, { 'form': form })
    
    def post(self, request, *args, **kwargs):
        form = CourseForm(request.POST, request.FILES)
        
        if form.is_valid():
            course = form.save(commit=False)
            course.teacher = request.user
            course.save()

            initial_capacity = form.cleaned_data.get('initial_capacity', 1)
            generate_timeslots_for_course(course, capacity=initial_capacity)
            if request.user.is_staff:
                return redirect('lessons')
            else:
                return redirect('teacher_dashboard')
           
        return render(request, self.template_name, {
            'form': form,
        })


def generate_timeslots_for_course(course, capacity=1, start_date=None, end_date=None, available_days=None, daily_start_time=None, daily_end_time=None):
    start_date = start_date or course.start_date
    end_date = end_date or course.end_date
    daily_start_time = daily_start_time or course.daily_start_time
    daily_end_time = daily_end_time or course.daily_end_time

    if not start_date or not end_date:
        return
    if not daily_start_time or not daily_end_time:
        return

    
    if available_days is None:
        raw = (course.available_days or "").strip()
        parts = []
        try:
            if raw.startswith('['):
                data = ast.literal_eval(raw)
                if isinstance(data, (list, tuple)):
                    parts = [str(x) for x in data]
                else:
                    parts = [str(data)]
            else:
                parts = [p.strip() for p in raw.split(',') if p.strip()]
        except Exception as e:
            cleaned = raw.replace('[', '').replace(']', '').replace('"', '').replace("'", "")
            parts = [p.strip() for p in cleaned.split(',') if p.strip()]
        allowed_days = [int(d) for d in parts if str(d).isdigit()]
    else:
        allowed_days = [int(d) for d in available_days]

    
    if not allowed_days:
        return 
    
    duration = timedelta(minutes=course.duration_minutes or 60)
    current_day = start_date
    while current_day <= end_date:
        if current_day.weekday() in allowed_days:
            day_start = datetime.combine(current_day, daily_start_time)
            day_end = datetime.combine(current_day, daily_end_time)

            slot_start = day_start
            while slot_start + duration <= day_end:
                TimeSlot.objects.update_or_create(
                    course=course,
                    start_time=slot_start,
                    # end_time=slot_start + duration,
                    defaults={
                        'end_time': slot_start + duration,
                        'capacity': capacity,
                        }
                )
                slot_start += duration
        current_day += timedelta(days=1)
    

    



class WeeklyScheduleView(LoginRequiredMixin, TemplateView):
    template_name = 'course/weekly_schedule.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        course = get_object_or_404(Course, pk=kwargs['pk'])
        ctx['course'] = course
        start_str = self.request.GET.get('start')
        if start_str:
            try:
                week_start = datetime.strptime(start_str, '%Y-%m-%d').date()
            except ValueError:
                today = timezone.localdate()
                week_start = today - timedelta(days=today.weekday())
        else:
            today = timezone.localdate()
            week_start = today - timedelta(days=today.weekday())
            
        week_end = week_start + timedelta(days=7)

        now = timezone.now()
        timeslots = (
            course.time_slots
            .filter(start_time__date__gte=week_start, 
            start_time__date__lt=week_end,
            start_time__gte=now,
            )
            .select_related('course')
            .prefetch_related('bookings')
        )

        slot_map = {}
        for ts in timeslots:
            date = ts.start_time.date()
            hour = ts.start_time.hour
            if week_start <= date < week_end:
                slot_map[(date, hour)] = ts
        days = [week_start + timedelta(days=i) for i in range(7)]
        ctx['days'] = days

        hours = []
        for h in range(24):
            row_cells = []
            for d in days:
                ts = slot_map.get((d, h))
                if ts: 
                    status = 'available' if ts.is_available else 'full'
                else:
                    status = 'empty'
                row_cells.append({
                    'date': d,
                    'slot': ts,
                    'status': status,
                })
            hours.append({ 'hour': h, 'cells': row_cells })
        ctx['hours'] = hours
        ctx['week_start'] = week_start
        ctx['week_end'] = week_end - timedelta(days=1)

        ctx['prev_start'] = week_start -timedelta(days=7)
        ctx['next_start'] = week_start + timedelta(days=7)
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

# @login_required(login_url='my_login')
# def my_bookings(request):
#     s_bookings = (
#         Booking.objects
#         .filter(student=request.user)
#         .select_related('timeslot', 'timeslot__course', 'timeslot__course__teacher')
#         .order_by('-timeslot__start_time'))
#     now = timezone.now()
#     for b in s_bookings:
#         b.can_cancel = (
#             b.status.lower() == "confirmed" and
#             b.timeslot.start_time > now + timedelta(hours=24))
#     upcoming_bookings = s_bookings.filter(
#         status__iexact="confirmed",
#         timeslot__start_time__gte=now
#     )
#     completed_bookings = s_bookings.filter(
#         status__iexact="confirmed",
#         timeslot__start_time__lt=now
#     )
#     canceled_bookings = s_bookings.filter(
#         status__iexact="canceled"
#     )
#     for b in s_bookings:
#         print(b.id, b.status, b.can_cancel)

    
#     return render(request, 'course/my_bookings.html', {
#         'upcoming_bookings': upcoming_bookings,
#         'completed_bookings': completed_bookings,
#         'canceled_bookings': canceled_bookings,
#     })



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
    cart = request.session.get('cart', [])
    if request.method != 'POST' or not cart:
        messages.error(request, "Your cart is empty.")
        return redirect('course:view_cart')

    slots = TimeSlot.objects.filter(pk__in=cart).select_related('course')
    if not slots.exists():
        messages.error(request, "Your cart is empty.")
        return redirect('course:view_cart')

    YOUR_DOMAIN = request.build_absolute_uri('/')[:-1]

    line_items = []
    timeslot_ids = []

    for slot in slots:
        line_items.append({
        'price_data': {
        'currency': 'usd',
        'unit_amount': int(slot.course.price * 100), 
        'product_data': {
        'name': f"{slot.course.title} - {slot.start_time}",
        },
        },
        'quantity': 1,
        })
        timeslot_ids.append(str(slot.pk))

    checkout_session = stripe.checkout.Session.create(
    payment_method_types=['card'],
    mode='payment',
    customer_email=request.user.email or None,
    line_items=line_items,
    metadata={
    'timeslot_ids': ','.join(timeslot_ids),
    'user_id': request.user.id,
    },
    success_url=YOUR_DOMAIN + reverse('course:cart_payment_success') + '?session_id={CHECKOUT_SESSION_ID}',
    cancel_url=YOUR_DOMAIN + reverse('course:cart_payment_cancel'),
    )

    request.session['cart'] = []
    request.session.modified = True

    return redirect(checkout_session.url)



@login_required(login_url='my_login')
def cart_payment_success(request):
    session_id = request.GET.get('session_id')
    if not session_id:
        messages.error(request, "Missing payment session.")
        return redirect('course:course_list')

    session = stripe.checkout.Session.retrieve(session_id)
    payment_intent_id = session.payment_intent
    timeslot_ids = session.metadata["timeslot_ids"].split(',') 

    if not timeslot_ids:
        messages.error(request, "No time slots found in payment session.")
        return redirect('course:course_list')

    now = timezone.now()
    created_bookings = []

    with transaction.atomic():
        slots = (TimeSlot.objects
        .select_for_update()
        .filter(pk__in=timeslot_ids)
        .annotate(booked_count=Count('bookings', filter=Q(bookings__status='confirmed')))
        .select_related('course', 'course__teacher'))
        slot_map = {str(slot.pk): slot for slot in slots}

    for ts_id in timeslot_ids:
        slot = slot_map.get(str(ts_id))
        if not slot:
            continue
        
        booking, created = Booking.objects.get_or_create(
            student=request.user,
            timeslot=slot,
            defaults={
                'status': 'confirmed', 
                'stripe_payment_intent_id': payment_intent_id,
                'stripe_session_id': session_id,
                'paid_at': timezone.now(),
                })
        if created:
            created_bookings.append(booking)
        else:
            booking.status = 'confirmed'
            booking.stripe_payment_intent_id = payment_intent_id
            booking.stripe_session_id = session_id
            booking.paid_at = timezone.now()
            booking.canceled_at = None
            booking.is_refunded = False
            booking.save(update_fields=[
                'status',
                'stripe_payment_intent_id',
                'stripe_session_id',
                'paid_at',
                'canceled_at',
                'is_refunded',
            ])
            created_bookings.append(booking)
        
            
        
    if not created_bookings:
        messages.info(request, "No new bookings were created. You may have already booked these classes.")
        return redirect('course:view_cart')
    
    for booking in created_bookings:
        teacher = booking.timeslot.course.teacher
        if teacher.email:
            send_mail(
                "New Class Booking Confirmed",
                (
                    f"Dear {teacher.first_name},\n\n"
                    f"A new booking has been confirmed for your course '{booking.timeslot.course.title}'.\n"
                    f"Student: {request.user.first_name} {request.user.last_name}\n"
                    f"Time: {booking.timeslot.start_time.strftime('%Y-%m-%d %H:%M')}\n\n"
                    f"Please contact the student within 24 hours to proceed with the class arrangements.\n\n"
                    f"Student Contact Email: {request.user.email}\n\n"
                    f"Best regards, \n"
                    f"PandaSpeak Support Team"
                ),
                settings.DEFAULT_FROM_EMAIL,
                [teacher.email],
                fail_silently=True,
            )  
    lines = []
    for booking in created_bookings:
        slot = booking.timeslot
        lines.append(
            f"Course: {slot.course.title}\n"
            f"Time: {slot.start_time.strftime('%Y-%m-%d %H:%M')}\n"
            f"Teacher: {slot.course.teacher.first_name} {slot.course.teacher.last_name}\n"

        )
    send_mail(
        "Your Class Booking Confirmation",
        (
            f"Dear {request.user.first_name} {request.user.last_name},\n\n"
            f"Your payment was successful and the following classes have been booked:\n\n"
            f"{chr(10).join(lines)}\n\n"
            f"The teacher will contact you shortly to proceed with the class arrangements.\n\n" 
            f"In any event if the teacher does not reach out within 24 hours, please contact us immediately so we can assist you.\n\n" 
            f"Best regards, \n"
            f"PandaSpeak Support Team"
        ),
        settings.DEFAULT_FROM_EMAIL,
        [request.user.email],
        fail_silently=True,
    )
            

    messages.success(request, "Payment successful. Your classes have been booked!")
    return redirect('course:course_list') 



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
                f"Your booking for the class '{slot.course.title}' scheduled on {slot.start_time.strftime('%Y-%m-%d %H:%M')} has been successfully cancelled.\n\n"
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
                f"Dear {teacher.first_name} {teacher.last_name},\n\n"
                f"The booking for your class '{slot.course.title}' scheduled on {slot.start_time.strftime('%Y-%m-%d %H:%M')} has been cancelled by the student.\n\n"
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




