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

        # Add the expanded Han dynasty story collection to the same dynamic
        # History Journey. Only the four requested stories are Level II; every
        # other Han story, including the existing Silk Road overview, is Level III.
        from . import history_views
        from .han_history_lessons import HAN_HISTORY_LESSONS, HAN_CARDS

        history_views.HISTORY_LESSONS.update(HAN_HISTORY_LESSONS)

        # Avoid duplicates if Django's app registry is initialized more than once
        # in a development process.
        han_slugs = {card['slug'] for card in HAN_CARDS}
        history_views.HISTORY_CARDS[:] = [
            card for card in history_views.HISTORY_CARDS if card['slug'] not in han_slugs
        ]

        # The original general Han/Silk Road lesson remains useful, but it is not
        # one of the four Level II stories requested for the Han dynasty.
        existing_han = history_views.HISTORY_LESSONS.get('han-silk-road')
        if existing_han:
            existing_han['level'] = 'level3'

        # Place the new Han stories immediately after the existing Han/Silk Road
        # overview and before later dynasties in the chronological master list.
        insert_at = next(
            (i + 1 for i, card in enumerate(history_views.HISTORY_CARDS)
             if card['slug'] == 'han-silk-road'),
            len(history_views.HISTORY_CARDS),
        )
        history_views.HISTORY_CARDS[insert_at:insert_at] = HAN_CARDS

        for dynasty in history_views.DYNASTIES:
            if dynasty['slug'] == 'han':
                dynasty['description'] = (
                    'From the Chu–Han struggle and early imperial consolidation to '
                    'Silk Road exchange, Eastern Han achievements, and the dynasty’s fall.'
                )
                dynasty['story_slugs'] = [
                    'hongmen-banquet',
                    'songs-of-chu',
                    'farewell-my-concubine',
                    'han-xin-humiliation',
                    'secret-chencang',
                    'xiao-he-pursues-han-xin',
                    'wen-jing-prosperity',
                    'tiying-saves-father',
                    'han-silk-road',
                    'zhang-qian-western-regions',
                    'wei-qing-huo-qubing',
                    'fenglangjuxu',
                    'su-wu-shepherd',
                    'li-guang',
                    'sima-qian-shiji',
                    'wang-zhaojun',
                    'guangwu-restoration',
                    'throw-brush-join-army',
                    'tiger-den',
                    'ban-chao-western-regions',
                    'cai-lun-paper',
                    'zhang-heng-seismoscope',
                    'yellow-turban-rebellion',
                    'dong-zhuo-chaos',
                ]
                break
