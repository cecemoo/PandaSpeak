from django.apps import AppConfig


class StudentConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'student'

    def ready(self):
        # Keep the main cultural view compact while allowing the catalog to grow.
        # Extra cards/lessons are merged before requests and template tags use them.
        from . import culture_views
        from .culture_extra_lessons import install
        install(culture_views)
