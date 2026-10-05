from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from subscription.plan_access import is_plus

from .history_lessons import HISTORY_CARDS as EXISTING_HISTORY_CARDS, HISTORY_LESSONS as EXISTING_HISTORY_LESSONS
from .early_history_lessons import EARLY_AFTER_ORACLE, EARLY_BEFORE_ORACLE, EARLY_HISTORY_LESSONS
from .history_media import media_for_lesson
from .models import HistoryLessonCompletion


# Build one chronological History Journey while keeping the existing lessons intact.
HISTORY_LESSONS = {**EXISTING_HISTORY_LESSONS, **EARLY_HISTORY_LESSONS}
_oracle_card = EXISTING_HISTORY_LESSONS['oracle-bones']
HISTORY_CARDS = (
    EARLY_BEFORE_ORACLE
    + [_oracle_card]
    + EARLY_AFTER_ORACLE
    + [card for card in EXISTING_HISTORY_CARDS if card['slug'] != 'oracle-bones']
)

HISTORY_PREVIEW_SLUG = 'oracle-bones'

# A story about the fall of a dynasty belongs to the dynasty that is ending.
DYNASTIES = [
    {'slug': 'xia', 'name': 'Xia Dynasty', 'chinese_name': '夏朝', 'dates': 'c. 2070–1600 BCE', 'icon': '🌊', 'description': 'Early dynastic tradition, Yu the Great, revival, and the fall of Xia.', 'story_slugs': ['yu-controls-floods', 'shao-kang-revival', 'shang-tang-overthrows-xia']},
    {'slug': 'shang', 'name': 'Shang Dynasty', 'chinese_name': '商朝', 'dates': 'c. 1600–1046 BCE', 'icon': '🐉', 'description': 'Oracle bones, early writing, bronze culture, and the fall of Shang.', 'story_slugs': ['oracle-bones', 'king-wu-overthrows-shang']},
    {'slug': 'zhou', 'name': 'Zhou Dynasty', 'chinese_name': '周朝', 'dates': '1046–256 BCE', 'icon': '🏹', 'description': 'Ritual, political order, the Mandate of Heaven, and the long Zhou era.', 'story_slugs': ['duke-of-zhou', 'beacon-fires']},
    {'slug': 'qin', 'name': 'Qin Dynasty', 'chinese_name': '秦朝', 'dates': '221–206 BCE', 'icon': '🧱', 'description': 'Unification, standardization, and the first imperial dynasty.', 'story_slugs': ['qin-unification']},
    {'slug': 'han', 'name': 'Han Dynasty', 'chinese_name': '漢朝', 'dates': '206 BCE–220 CE', 'icon': '🐫', 'description': 'Imperial expansion and the Silk Road.', 'story_slugs': ['han-silk-road']},
    {'slug': 'three-kingdoms', 'name': 'Three Kingdoms', 'chinese_name': '三國', 'dates': '220–280', 'icon': '⚔️', 'description': 'A famous age of competing states, strategy, and legendary figures.', 'story_slugs': []},
    {'slug': 'jin', 'name': 'Jin Dynasty', 'chinese_name': '晉朝', 'dates': '266–420', 'icon': '📜', 'description': 'Reunification followed by division and migration.', 'story_slugs': []},
    {'slug': 'northern-southern', 'name': 'Northern & Southern Dynasties', 'chinese_name': '南北朝', 'dates': '420–589', 'icon': '⛰️', 'description': 'A divided era of cultural exchange and political change.', 'story_slugs': []},
    {'slug': 'sui', 'name': 'Sui Dynasty', 'chinese_name': '隋朝', 'dates': '581–618', 'icon': '🌉', 'description': 'Reunification and major public works before the rise of Tang.', 'story_slugs': []},
    {'slug': 'tang', 'name': 'Tang Dynasty', 'chinese_name': '唐朝', 'dates': '618–907', 'icon': '🏮', 'description': 'Cosmopolitan Chang’an, poetry, trade, and cultural exchange.', 'story_slugs': ['tang-changan']},
    {'slug': 'five-dynasties', 'name': 'Five Dynasties & Ten Kingdoms', 'chinese_name': '五代十國', 'dates': '907–960', 'icon': '🗺️', 'description': 'A short but important period of political division.', 'story_slugs': []},
    {'slug': 'song', 'name': 'Song Dynasty', 'chinese_name': '宋朝', 'dates': '960–1279', 'icon': '🧭', 'description': 'Innovation, commerce, cities, printing, and new technologies.', 'story_slugs': ['song-innovation']},
    {'slug': 'yuan', 'name': 'Yuan Dynasty', 'chinese_name': '元朝', 'dates': '1271–1368', 'icon': '🐎', 'description': 'Mongol rule and connections across Eurasia.', 'story_slugs': []},
    {'slug': 'ming', 'name': 'Ming Dynasty', 'chinese_name': '明朝', 'dates': '1368–1644', 'icon': '⛵', 'description': 'Maritime voyages, rebuilding, and a flourishing imperial culture.', 'story_slugs': ['zheng-he']},
    {'slug': 'qing', 'name': 'Qing Dynasty', 'chinese_name': '清朝', 'dates': '1644–1912', 'icon': '🏯', 'description': 'The last imperial dynasty and the transformation toward the modern era.', 'story_slugs': ['ming-qing-beijing']},
    {'slug': 'modern', 'name': 'Modern China & Taiwan', 'chinese_name': '近現代中國與臺灣', 'dates': '1912–Present', 'icon': '🌏', 'description': 'Modern change, society, identity, and the Chinese-speaking world today.', 'story_slugs': ['modern-and-taiwan']},
]


def _allowed_history_levels(user):
    if user.is_staff or user.is_superuser:
        return ('level2', 'level3')
    level = getattr(user, 'learning_level', 'level1') or 'level1'
    if level == 'level3':
        return ('level2', 'level3')
    if level == 'level2':
        return ('level2',)
    return ()


def _lesson_items(user, allowed, plus_active):
    completed_slugs = set(HistoryLessonCompletion.objects.filter(student=user).values_list('lesson_slug', flat=True))
    items = []
    for card in HISTORY_CARDS:
        if card['level'] in allowed:
            item = card.copy()
            item['completed'] = item['slug'] in completed_slugs
            item['is_preview'] = item['slug'] == HISTORY_PREVIEW_SLUG
            item['plus_locked'] = not plus_active and not item['is_preview']
            items.append(item)
    return items


def _dynasty_for_story(story_slug):
    return next((dynasty for dynasty in DYNASTIES if story_slug in dynasty['story_slugs']), None)


@login_required
def chinese_history(request):
    level = getattr(request.user, 'learning_level', 'level1') or 'level1'
    allowed = _allowed_history_levels(request.user)
    plus_active = is_plus(request.user)
    if not allowed:
        return render(request, 'student/chinese_history.html', {'level_locked': True, 'dynasties': [], 'student_level': level, 'completed_count': 0, 'total_count': 0, 'plus_active': plus_active, 'preview_slug': HISTORY_PREVIEW_SLUG})

    lessons = _lesson_items(request.user, allowed, plus_active)
    by_slug = {item['slug']: item for item in lessons}
    dynasties = []
    for dynasty in DYNASTIES:
        item = dynasty.copy()
        stories = [by_slug[s] for s in dynasty['story_slugs'] if s in by_slug]
        item['stories'] = stories
        item['story_count'] = len(stories)
        item['completed_count'] = sum(1 for story in stories if story['completed'])
        item['available'] = bool(stories)
        dynasties.append(item)

    accessible_lessons = [item for item in lessons if not item['plus_locked']]
    return render(request, 'student/chinese_history.html', {
        'level_locked': False, 'dynasties': dynasties, 'student_level': level,
        'completed_count': sum(1 for item in accessible_lessons if item['completed']),
        'total_count': len(accessible_lessons), 'plus_active': plus_active,
        'preview_slug': HISTORY_PREVIEW_SLUG,
    })


@login_required
def history_dynasty_detail(request, dynasty_slug):
    allowed = _allowed_history_levels(request.user)
    if not allowed:
        return redirect('chinese_history')
    dynasty = next((d for d in DYNASTIES if d['slug'] == dynasty_slug), None)
    if not dynasty:
        return redirect('chinese_history')
    plus_active = is_plus(request.user)
    lessons = _lesson_items(request.user, allowed, plus_active)
    by_slug = {item['slug']: item for item in lessons}
    stories = [by_slug[s] for s in dynasty['story_slugs'] if s in by_slug]
    dynasty = dynasty.copy()
    dynasty['stories'] = stories
    dynasty['completed_count'] = sum(1 for story in stories if story['completed'])
    return render(request, 'student/history_dynasty_detail.html', {'dynasty': dynasty, 'plus_active': plus_active})


@login_required
def history_lesson_detail(request, slug):
    lesson = HISTORY_LESSONS.get(slug)
    admin_access = request.user.is_staff or request.user.is_superuser
    if not lesson or (lesson['level'] not in _allowed_history_levels(request.user) and not admin_access):
        return redirect('chinese_history')
    if slug != HISTORY_PREVIEW_SLUG and not is_plus(request.user) and not admin_access:
        return redirect('plus_upgrade')

    completion = HistoryLessonCompletion.objects.filter(student=request.user, lesson_slug=slug).first()
    completed = completion is not None
    result = None
    selected = None

    if request.method == 'POST':
        selected = request.POST.get('answer')
        if selected:
            result = selected == lesson['quiz']['answer']
            if result:
                completion, _ = HistoryLessonCompletion.objects.get_or_create(student=request.user, lesson_slug=slug)
                completed = True

    plus_active = is_plus(request.user)
    return render(request, 'student/history_lesson_detail.html', {
        'lesson': lesson,
        'slug': slug,
        'media': media_for_lesson(slug),
        'quiz_result': result,
        'selected_answer': selected,
        'completed': completed,
        'completed_at': completion.completed_at if completion else None,
        'is_preview': slug == HISTORY_PREVIEW_SLUG and not plus_active,
        'plus_active': plus_active,
        'dynasty': _dynasty_for_story(slug),
    })
