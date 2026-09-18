from datetime import timedelta

from django.db import models
from account.models import CustomUser
from django.utils import timezone
from django.conf import settings

WEEKDAY_CHOICES = [(0,'Monday'),(1,'Tuesday'),(2,'Wednesday'),(3,'Thursday'),(4,'Friday'),(5,'Saturday'),(6,'Sunday')]

class Course(models.Model):
    SESSION_TYPE_CHOICES = (('private','Private Tutoring'),('group','Group Tutoring'))
    ENROLLMENT_STATUS_CHOICES = (('open','Open for Enrollment'),('confirmed','Confirmed'),('proceed','Proceed Below Minimum'),('canceled','Canceled'))
    teacher = models.ForeignKey(CustomUser,on_delete=models.CASCADE,related_name='courses')
    title = models.CharField(max_length=200)
    description = models.TextField()
    image = models.ImageField(upload_to='course_images/',blank=True,null=True)
    video_url = models.URLField(blank=True,null=True)
    price = models.PositiveIntegerField()
    duration_minutes = models.PositiveIntegerField(default=60)
    session_type = models.CharField(max_length=10,choices=SESSION_TYPE_CHOICES,default='private')
    max_students = models.PositiveIntegerField(default=1,help_text='Maximum number of students who can book the same session.')
    minimum_students = models.PositiveIntegerField(default=1,help_text='Minimum paid students required for a group class to proceed.')
    enrollment_status = models.CharField(max_length=12,choices=ENROLLMENT_STATUS_CHOICES,default='open')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    start_date = models.DateField(blank=True,null=True)
    end_date = models.DateField(blank=True,null=True)
    available_days = models.CharField(max_length=100,blank=True,help_text='Comma separated weekdays (0=Monday, 6=Sunday)')
    daily_start_time = models.TimeField(blank=True,null=True)
    daily_end_time = models.TimeField(blank=True,null=True)
    teacher_timezone = models.CharField(max_length=64,default='America/Chicago',help_text='Time zone used when creating this course schedule.')
    def __str__(self): return self.title
    @property
    def is_group_session(self): return self.session_type == 'group'
    @property
    def enrollment_deadline(self):
        return self.start_date - timedelta(days=5) if self.session_type == 'group' and self.start_date else None
    @property
    def paid_student_count(self):
        return Booking.objects.filter(timeslot__course=self,status='confirmed',paid_at__isnull=False,is_refunded=False).values('student_id').distinct().count()
    @property
    def minimum_enrollment_reached(self):
        return self.session_type != 'group' or self.paid_student_count >= self.minimum_students
    @property
    def enrollment_is_open(self):
        if self.session_type != 'group': return True
        if self.enrollment_status == 'canceled': return False
        deadline = self.enrollment_deadline
        return not deadline or timezone.localdate() <= deadline
    @property
    def needs_enrollment_decision(self):
        return self.session_type == 'group' and self.enrollment_deadline and timezone.localdate() > self.enrollment_deadline and not self.minimum_enrollment_reached and self.enrollment_status == 'open'
    def save(self,*args,**kwargs):
        if self.session_type == 'private':
            self.max_students = 1; self.minimum_students = 1; self.enrollment_status = 'confirmed'
        else:
            if self.max_students < 2: self.max_students = 2
            if self.minimum_students < 2: self.minimum_students = 2
            if self.minimum_students > self.max_students: self.minimum_students = self.max_students
        if self.video_url and 'drive.google.com/file/d/' in self.video_url:
            self.video_url = self.video_url.replace('/view?usp=sharing','/preview').replace('/view','/preview')
        super().save(*args,**kwargs)

class TimeSlot(models.Model):
    course = models.ForeignKey(Course,on_delete=models.CASCADE,related_name='time_slots')
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    capacity = models.PositiveIntegerField()
    def __str__(self): return f'{self.course.title} - {self.start_time}'
    @property
    def remaining_slots(self): return max(self.capacity-self.bookings.filter(status='confirmed').count(),0)
    @property
    def is_available(self): return self.remaining_slots > 0 and self.course.enrollment_is_open

class Booking(models.Model):
    STATUS_CHOICES=(('pending','Pending'),('confirmed','Confirmed'),('canceled','Canceled'))
    SESSION_STATUS_CHOICES=(('scheduled','Scheduled'),('in_progress','In Progress'),('completed','Completed'),('review_required','Review Required'),('disputed','Disputed'),('no_show_student','Student No-show'),('no_show_teacher','Teacher No-show'))
    PAYOUT_STATUS_CHOICES=(('pending','Pending'),('awaiting_release','Awaiting Release'),('on_hold','On Hold'),('transferred','Transferred'),('reversed','Reversed'))
    student=models.ForeignKey(CustomUser,on_delete=models.CASCADE,related_name='bookings')
    timeslot=models.ForeignKey(TimeSlot,on_delete=models.CASCADE,related_name='bookings')
    status=models.CharField(max_length=10,choices=STATUS_CHOICES,default='pending')
    stripe_session_id=models.CharField(max_length=255,blank=True,null=True)
    paid_at=models.DateTimeField(blank=True,null=True)
    created_at=models.DateTimeField(auto_now_add=True)
    canceled_at=models.DateTimeField(blank=True,null=True)
    stripe_payment_intent_id=models.CharField(max_length=255,blank=True,null=True)
    stripe_transfer_id=models.CharField(max_length=255,blank=True,null=True)
    teacher_transfer_amount_cents=models.PositiveIntegerField(default=0)
    is_refunded=models.BooleanField(default=False)
    is_test_booking=models.BooleanField(default=False)
    session_status=models.CharField(max_length=30,choices=SESSION_STATUS_CHOICES,default='scheduled')
    meeting_room_id=models.CharField(max_length=120,blank=True,null=True,unique=True)
    session_started_at=models.DateTimeField(blank=True,null=True)
    session_completed_at=models.DateTimeField(blank=True,null=True)
    shared_minutes=models.PositiveIntegerField(default=0)
    payout_status=models.CharField(max_length=20,choices=PAYOUT_STATUS_CHOICES,default='pending')
    payout_eligible_at=models.DateTimeField(blank=True,null=True)
    payout_transferred_at=models.DateTimeField(blank=True,null=True)
    student_reported_issue=models.BooleanField(default=False)
    issue_details=models.TextField(blank=True)
    issue_reported_at=models.DateTimeField(blank=True,null=True)
    issue_resolved_at=models.DateTimeField(blank=True,null=True)
    issue_resolution_note=models.TextField(blank=True)
    review_rating=models.PositiveSmallIntegerField(blank=True,null=True)
    review_comment=models.TextField(blank=True)
    reviewed_at=models.DateTimeField(blank=True,null=True)
    reminder_24h_sent_at=models.DateTimeField(blank=True,null=True)
    reminder_1h_sent_at=models.DateTimeField(blank=True,null=True)
    class Meta:
        constraints=[models.UniqueConstraint(fields=['student','timeslot'],name='unique_booking_per_student_timeslot')]
        indexes=[models.Index(fields=['student','status']),models.Index(fields=['timeslot','status']),models.Index(fields=['session_status','payout_status'])]
    @property
    def is_archived_from_tutoring_lists(self):
        if self.session_status!='completed' or self.payout_status!='transferred' or not self.payout_transferred_at: return False
        return self.payout_transferred_at <= timezone.now()-timedelta(days=7)
    def cancel(self):
        if self.status!='canceled':
            self.status='canceled'; self.canceled_at=timezone.now(); self.save(update_fields=['status','canceled_at'])
    def __str__(self): return f'{self.student.email} -> {self.timeslot}'

class SessionAttendance(models.Model):
    booking=models.ForeignKey(Booking,on_delete=models.CASCADE,related_name='attendance_records')
    user=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE,related_name='tutoring_attendance_records')
    joined_at=models.DateTimeField(auto_now_add=True)
    last_seen_at=models.DateTimeField(default=timezone.now)
    left_at=models.DateTimeField(blank=True,null=True)
    class Meta:
        indexes=[models.Index(fields=['booking','user','joined_at'])]
        ordering=['joined_at']
    def __str__(self): return f'{self.user} in booking {self.booking_id}'

class StudentGroup(models.Model):
    name=models.CharField(max_length=100)
    teacher=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE,related_name='student_groups')
    students=models.ManyToManyField(settings.AUTH_USER_MODEL,related_name='groups_joined',blank=True)
    is_active=models.BooleanField(default=True)
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)
    def __str__(self): return self.name

class GroupClassRequest(models.Model):
    STATUS_CHOICES=(('pending','Pending'),('accepted','Accepted'),('declined','Declined'),('converted','Class Created'))
    LEVEL_CHOICES=(('level1','Level I'),('level2','Level II'),('level3','Level III'))
    student=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE,related_name='group_class_requests')
    teacher=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE,related_name='group_class_requests_received')
    source_course=models.ForeignKey(Course,on_delete=models.SET_NULL,blank=True,null=True,related_name='group_class_requests')
    topic=models.CharField(max_length=200)
    level=models.CharField(max_length=10,choices=LEVEL_CHOICES,default='level1')
    preferred_times=models.CharField(max_length=500)
    desired_group_size=models.PositiveIntegerField(default=4)
    requested_price=models.PositiveIntegerField(blank=True,null=True,help_text='Price per student proposed by the student.')
    message=models.TextField(blank=True)
    status=models.CharField(max_length=12,choices=STATUS_CHOICES,default='pending')
    created_course=models.ForeignKey(Course,on_delete=models.SET_NULL,blank=True,null=True,related_name='originating_group_requests')
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)
    class Meta:
        ordering=['-created_at']
        indexes=[models.Index(fields=['teacher','status']),models.Index(fields=['student','status'])]
    def __str__(self): return f'{self.student} -> {self.teacher}: {self.topic}'
