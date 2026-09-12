from django.apps import AppConfig


class CourseConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'course'

    def ready(self):
        # RescheduleRequest lives in a separate module to keep tutoring
        # rescheduling logic isolated while still registering the model.
        from . import reschedule_models  # noqa: F401
