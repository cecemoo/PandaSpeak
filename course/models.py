from django.db import models
from account.models import CustomUser
from django.utils import timezone





WEEKDAY_CHOICES = [
    (0, 'Monday'),
    (1, 'Tuesday'),
    (2, 'Wednesday'),
    (3, 'Thursday'),
    (4, 'Friday'),
    (5, 'Saturday'),
    (6, 'Sunday'),
]


class Course(models.Model):
    teacher = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='courses')
    title = models.CharField(max_length=200)
    description = models.TextField()
    image = models.ImageField(upload_to='course_images/', blank=True, null=True)
    video_url = models.URLField(blank=True, null=True)
    price = models.PositiveIntegerField()
    duration_minutes = models.PositiveIntegerField(default=60)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)
    available_days = models.CharField(max_length=100, blank=True, help_text='Comma separated weekdays (0=Monday, 6=Sunday)')
    daily_start_time = models.TimeField(blank=True, null=True)
    daily_end_time = models.TimeField(blank=True, null=True)
   
    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if self.video_url and "drive.google.com/file/d/" in self.video_url:
            self.video_url = (
                self.video_url
                .replace("/view?usp=sharing", "/preview")
                .replace("/view", "/preview")
            )
        super().save(*args, **kwargs)


        

class TimeSlot(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='time_slots')
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    capacity = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.course.title} - {self.start_time}"

    @property
    def remaining_slots(self):
        booked_count = self.bookings.filter(status='confirmed').count()
        return max(self.capacity - booked_count, 0)
    
    @property
    def is_available(self):
        return self.remaining_slots > 0
    

class Booking(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('canceled', 'Canceled'),
    )

    student = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='bookings')
    timeslot = models.ForeignKey(TimeSlot, on_delete=models.CASCADE, related_name='bookings')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    stripe_session_id = models.CharField(max_length=255, blank=True, null=True)
    paid_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    canceled_at = models.DateTimeField(blank=True, null=True)

    stripe_payment_intent_id = models.CharField(max_length=255, blank=True, null=True)
    is_refunded = models.BooleanField(default=False)

    class Meta:
        constraints = [models.UniqueConstraint(fields=['student', 'timeslot'], name='unique_booking_per_student_timeslot')]
        indexes = [models.Index(fields=['student', 'status']), models.Index(fields=['timeslot', 'status'])]

    def cancel(self):
        if self.status != 'canceled':
            self.status = 'canceled'
            self.canceled_at = timezone.now()
            self.save(update_fields=['status', 'canceled_at'])

    def __str__(self):
        return f"{self.student.username} -> {self.timeslot}"
