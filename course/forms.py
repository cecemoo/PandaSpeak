from django import forms
from .models import Course, TimeSlot, WEEKDAY_CHOICES
from django.forms import inlineformset_factory
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.core.exceptions import ObjectDoesNotExist
from datetime import time
from zoneinfo import available_timezones


COMMON_TIMEZONE_CHOICES = [
    ("America/Chicago", "Houston /Chicago"),
    ("America/New_York", "New York"),
    ("America/Los_Angeles", "Los Angeles"),
    ("America/Denver", "Denver"),
    ("America/Phoenix", "Phoenix"),
    ("Pacific/Honolulu", "Hawaii"),
    ("Asia/Tokyo", "Tokyo"),
    ("Asia/Shanghai", "Shanghai"),
    ("Asia/Singapore", "Singapore"),
    ("Asia/Taipei", "Taipei"),
    ("Asia/Seoul", "Seoul"),
    ("Asia/Beijing", "Beijing"),
    ("Europe/London", "London"),
    ("Europe/Paris", "Paris"),
    ("Australia/Sydney", "Sydney"),
]



HOUR_CHOICES = [(f"{h:02d}:00", f"{h:02d}:00") for h in range(24)]

class CourseForm(forms.ModelForm):
    available_days = forms.MultipleChoiceField(choices=WEEKDAY_CHOICES,widget=forms.CheckboxSelectMultiple,required=True,label='Teaching days',)
    initial_capacity = forms.IntegerField(min_value=1,initial=1,required=True,label="Capacity per time slot",help_text="Set the maximum number of students allowed in each time slot. ")
    daily_start_time = forms.ChoiceField(choices=HOUR_CHOICES, required=True, label="Daily start time", widget=forms.Select(),)
    daily_end_time = forms.ChoiceField(choices=HOUR_CHOICES, required=True, label="Daily end time", widget=forms.Select(),)
    teacher_timezone = forms.ChoiceField(
        choices=COMMON_TIMEZONE_CHOICES,
        initial="America/Chicago",
        required=True,
        label="Schedule time zone",
        help_text=(
            "Enter the teaching schedule in this time zone. "
            "Students will see it converted to their local time."
        ),
    )

    class Meta:
        model = Course
        fields = [
        'title',
        'description',
        'price',
        'duration_minutes',
        'image',
        'video_url',
        'start_date',
        'end_date',
        'available_days',
        'daily_start_time',
        'daily_end_time',
        "teacher_timezone",
        ]

        help_texts = {
            'duration_minutes': 'The weekly schedule table is designed in hourly time slots. if the lesson is less than one hour, such as 30 minutes, the timetable will still show one-hour availability.',
        }
       
        widgets = {
        'start_date': forms.DateInput(attrs={'type': 'date'}),
        'end_date': forms.DateInput(attrs={'type': 'date'}),
       
        }
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            if self.instance and self.instance.pk and self.instance.available_days:
                self.initial['available_days'] = self.instance.available_days.split(',')
        
        def clean(self):
            cleaned = super().clean()
            start_date = cleaned.get('start_date')
            end_date = cleaned.get('end_date')
            start_time = cleaned.get('daily_start_time')
            end_time = cleaned.get('daily_end_time')

            if start_date and end_date and end_date < start_date:
                raise ValidationError("End date must be on or after start date.")
            if start_time:
                h = int(start_time.split(':')[0])
                cleaned['daily_start_time'] = time(h, 0)
            if end_time:
                h = int(end_time.split(':')[0])
                cleaned['daily_end_time'] = time(h, 0)
            if cleaned.get('daily_start_time') and cleaned.get('daily_end_time'):
                if cleaned['daily_end_time'] <= cleaned['daily_start_time']:
                    raise ValidationError("Daily end time must be after daily start time.")

            return cleaned
        
        def save(self, commit=True):
            obj = super().save(commit=False)
            days = self.cleaned_data.get('available_days', [])
            obj.available_days = ','.join(days)
            if commit:
                obj.save()
            return obj


class GenerateMoreTimeSlotsForm(forms.Form):
    start_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    end_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    available_days = forms.MultipleChoiceField(choices=WEEKDAY_CHOICES,widget=forms.CheckboxSelectMultiple,required=True,label='Teaching days',)
    daily_start_time = forms.ChoiceField(choices=HOUR_CHOICES, required=True, label="Daily start time", widget=forms.Select(),)
    daily_end_time = forms.ChoiceField(choices=HOUR_CHOICES, required=True, label="Daily end time", widget=forms.Select(),)
    capacity = forms.IntegerField(min_value=1, initial=1, required=False)

    def clean(self):
        cleaned = super().clean()
        start_date = cleaned.get('start_date')
        end_date = cleaned.get('end_date')
        start_time = cleaned.get('daily_start_time')
        end_time = cleaned.get('daily_end_time')

        if start_date and end_date and end_date < start_date:
            raise ValidationError("End date must be on or after start date.")
        if start_time:
            h = int(start_time.split(':')[0])
            cleaned['daily_start_time'] = time(h, 0)
        if end_time:
            h = int(end_time.split(':')[0])
            cleaned['daily_end_time'] = time(h, 0)
        if cleaned.get('daily_start_time') and cleaned.get('daily_end_time'):
            if cleaned['daily_end_time'] <= cleaned['daily_start_time']:
                raise ValidationError("Daily end time must be after daily start time.")
        return cleaned


class TimeSlotForm(forms.ModelForm):
    start_time = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        input_formats=['%Y-%m-%dT%H:%M'],
    )
    end_time = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        input_formats=['%Y-%m-%dT%H:%M'],
    )
    class Meta:
        model = TimeSlot
        fields = ['capacity', 'start_time', 'end_time']
        labels = {
             'start_time' : 'Session start (date & time)',
                'end_time' : 'Session end (date & time)',
        }
    def __init__(self, *args, **kwargs):
        self.course = kwargs.pop("course", None)
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        start = cleaned_data.get('start_time')
        end = cleaned_data.get('end_time')

        if not start or not end:
            return cleaned_data

        if end <= start:
            raise ValidationError("End time must be after start time.")

        course = self.course
        if course is None:
            try:
                course = self.instance.course
            except ObjectDoesNotExist:
                course = None
        if course:
                if course.start_date and start.date() < course.start_date:
                    raise ValidationError(
        f"Time slot start time must be on or after {course.start_date}."
        )
                if course.end_date and start.date() > course.end_date:
                    raise ValidationError(
        f"Time slot start time must be on or before {course.end_date}."
        )

        return cleaned_data


TimeSlotFormSet = inlineformset_factory(
    Course,
    TimeSlot,
    form=TimeSlotForm,
    extra=5,
    can_delete=True,
)