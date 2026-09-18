import logging

import stripe
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.http import require_POST

from account.models import Notification
from .models import Booking, Course

logger = logging.getLogger(__name__)
stripe.api_key = settings.STRIPE_SECRET_KEY


def _name(user):
    return user.get_full_name().strip() or user.email or 'PandaSpeak User'


def _sync_status(course):
    if course.session_type == 'group' and course.enrollment_status == 'open' and course.minimum_enrollment_reached:
        course.enrollment_status = 'confirmed'
        course.save(update_fields=['enrollment_status','updated_at'])


@login_required
def group_enrollment(request, pk):
    course = get_object_or_404(Course, pk=pk, teacher=request.user, session_type='group')
    _sync_status(course)
    bookings = Booking.objects.filter(timeslot__course=course, status='confirmed', paid_at__isnull=False, is_refunded=False).select_related('student','timeslot').order_by('timeslot__start_time')
    return render(request, 'course/group_enrollment.html', {'course':course,'paid_bookings':bookings})


@login_required
@require_POST
def group_enrollment_decision(request, pk, decision):
    course = get_object_or_404(Course, pk=pk, teacher=request.user, session_type='group')
    _sync_status(course)
    if decision not in ('proceed','cancel'):
        messages.error(request, 'Invalid enrollment decision.')
        return redirect('course:group_enrollment', pk=course.pk)
    if course.minimum_enrollment_reached:
        messages.info(request, 'The minimum enrollment has already been reached. The class is confirmed.')
        return redirect('course:group_enrollment', pk=course.pk)
    if not course.enrollment_deadline or timezone.localdate() <= course.enrollment_deadline:
        messages.error(request, 'This decision becomes available after the enrollment deadline, 5 days before the class starts.')
        return redirect('course:group_enrollment', pk=course.pk)
    if decision == 'proceed':
        course.enrollment_status = 'proceed'; course.save(update_fields=['enrollment_status','updated_at'])
        students = {b.student for b in Booking.objects.filter(timeslot__course=course,status='confirmed',is_refunded=False).select_related('student')}
        for student in students:
            Notification.objects.create(user=student,title='Group Class Confirmed',message=f'“{course.title}” will proceed with the current enrollment.',link=reverse('course:my_bookings'))
            if student.email:
                send_mail('PandaSpeak - Group Class Confirmed',f'Dear {_name(student)},\n\nYour group class “{course.title}” has been confirmed and will proceed with the current enrollment.\n\nNo action is required. Please review your booking for the class schedule.\n\nBest regards,\nPandaSpeak Team',settings.DEFAULT_FROM_EMAIL,[student.email],fail_silently=True)
        messages.success(request, 'The group class is confirmed to proceed with the current enrollment.')
        return redirect('course:group_enrollment', pk=course.pk)

    bookings = list(Booking.objects.filter(timeslot__course=course,status='confirmed',paid_at__isnull=False,is_refunded=False).select_related('student','timeslot'))
    refunded = 0
    for booking in bookings:
        if not booking.stripe_payment_intent_id:
            logger.error('Cannot refund booking %s: missing PaymentIntent', booking.pk)
            continue
        try:
            stripe.Refund.create(payment_intent=booking.stripe_payment_intent_id, amount=int(booking.timeslot.course.price * 100), metadata={'booking_id':str(booking.pk),'reason':'group_minimum_not_reached'}, idempotency_key=f'group-minimum-refund-{booking.pk}')
        except stripe.error.StripeError:
            logger.exception('Refund failed for booking %s', booking.pk)
            continue
        booking.is_refunded=True; booking.status='canceled'; booking.canceled_at=timezone.now(); booking.payout_status='reversed'; booking.save(update_fields=['is_refunded','status','canceled_at','payout_status'])
        refunded += 1
        student=booking.student
        Notification.objects.create(user=student,title='Group Class Canceled and Refunded',message=f'“{course.title}” was canceled because minimum enrollment was not reached. Your class payment has been refunded.',link=reverse('course:my_bookings'))
        if student.email:
            send_mail('PandaSpeak - Group Class Canceled and Refunded',f'Dear {_name(student)},\n\nUnfortunately, “{course.title}” did not reach the minimum enrollment by the enrollment deadline and the teacher has canceled the class.\n\nPandaSpeak has issued a full refund of your class payment to your original payment method. Your bank or card issuer may take additional time to post the refund.\n\nWe apologize for the inconvenience and hope you will join another PandaSpeak class.\n\nBest regards,\nPandaSpeak Team',settings.DEFAULT_FROM_EMAIL,[student.email],fail_silently=True)
    if refunded == len(bookings):
        course.enrollment_status='canceled'; course.save(update_fields=['enrollment_status','updated_at'])
        messages.success(request, f'Class canceled. {refunded} paid booking(s) were fully refunded.')
    else:
        messages.error(request, f'{refunded} of {len(bookings)} refunds succeeded. The class was not marked canceled so the remaining refunds can be resolved safely.')
    return redirect('course:group_enrollment', pk=course.pk)
