from django.contrib import admin
from .models import Course, TimeSlot, Booking, StudentGroup
# Register your models here.


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('title', 'teacher', 'price', 'created_at')
    search_fields = ('title', 'description', 'teacher__username')
    list_filter = ('created_at',)   


@admin.register(TimeSlot)
class TimeSlotAdmin(admin.ModelAdmin):
    list_display = ('course', 'start_time', 'end_time', 'capacity')
    search_fields = ('course__title',)
    list_filter = ('start_time', 'end_time')


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('student', 'timeslot', 'status','is_refunded', 'created_at')
    search_fields = ('student__username', 'timeslot__course__title')


@admin.register(StudentGroup)
class StudentGroupAdmin(admin.ModelAdmin):
    list_display = ('name', 'teacher', 'is_active', 'created_at')
    search_fields = ('name', 'teacher__username')
    list_filter = ('is_active', 'created_at')
    