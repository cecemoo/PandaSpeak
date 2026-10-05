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

        # Qin history lessons have individual difficulty levels. Keep the more
        # accessible foundation/folk-story topics at Level II and assign the
        # politically, historically, or linguistically more complex stories to
        # Level III. The lesson dictionaries are shared by the history cards, so
        # this also updates the level badges and student access filtering.
        from .qin_history_lessons import QIN_HISTORY_LESSONS

        level3_qin_slugs = {
            'jing-ke-assassination',
            'burning-books',
            'sha-qiu-coup',
            'calling-deer-horse',
            'dazexiang-uprising',
            'battle-of-julu',
            'fall-of-qin',
        }
        for slug, lesson in QIN_HISTORY_LESSONS.items():
            lesson['level'] = 'level3' if slug in level3_qin_slugs else 'level2'
