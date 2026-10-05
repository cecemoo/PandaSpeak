"""Media files used by Chinese History lessons.

Keep lesson-to-media mapping here so the lesson template stays small and new
stories only require one entry when their video/audio is uploaded.
"""

HISTORY_MEDIA = {
    'yu-controls-floods': {
        'audio': 'student/history/yu-floods-discovery-narration.m4a',
        'video': 'student/history/yu-floods-1min.mp4',
    },
    'shao-kang-revival': {
        'audio': 'student/history/shao-kang-discovery-narration.m4a',
        'video': 'student/history/shao-kang-1min.mp4',
    },
    'shang-tang-overthrows-xia': {
        'audio': 'student/history/tang-xia-discovery-narration.m4a',
        'video': 'student/history/tang-xia-1min.mp4',
    },
    'oracle-bones': {
        'audio': 'student/history/oracle-bones.m4a',
        'video': 'student/history/oracle-bones.mp4',
    },
    'king-wu-overthrows-shang': {
        'audio': 'student/history/king-wu-discovery-narration.m4a',
        'video': 'student/history/king-wu-1min.mp4',
    },
    'duke-of-zhou': {
        'audio': 'student/history/duke-zhou-discovery-narration.m4a',
        'video': 'student/history/duke-zhou-1min.mp4',
    },
    'beacon-fires': {
        'audio': 'student/history/beacon-fires-discovery-narration.m4a',
        'video': 'student/history/beacon-fires-1min.mp4',
    },
    'jing-ke-assassination': {
        'audio': 'student/history/Qin/jing-ke-discover-narration.m4a',
        'video': 'student/history/Qin/jing-ke-1min.mp4',
    },
    'qin-unification': {
        'audio': 'student/history/qin_unification_listen.m4a',
        'video': 'student/history/PandaSpeak_Qin_Unification_v3.mp4',
        'video_version': 4,
    },
    'qin-standardization': {
        'audio': 'student/history/Qin/qin-standardization-discover-narration.m4a',
        'video': 'student/history/Qin/qin-standardization-1min.mp4',
    },
    'qin-great-wall': {
        'audio': 'student/history/Qin/qin-great-wall-discover-narration.m4a',
        'video': 'student/history/Qin/qin-great-wall-1min.mp4',
    },
    'meng-jiangnu': {
        'audio': 'student/history/Qin/meng-jiangnu-discover-narration.m4a',
        'video': 'student/history/Qin/meng-jiangnu-1min.mp4',
    },
    'burning-books': {
        'audio': 'student/history/Qin/burning-books-discover-narration.m4a',
        'video': 'student/history/Qin/burning-books-1min.mp4',
    },
    'sha-qiu-coup': {
        'audio': 'student/history/Qin/shaqiu-coup-discover-narration.m4a',
        'video': 'student/history/Qin/shaqiu-coup-1min.mp4',
    },
    'calling-deer-horse': {
        'audio': 'student/history/Qin/deer-horse-discover-narration.m4a',
        'video': 'student/history/Qin/deer-horse-1min.mp4',
    },
    'han-silk-road': {
        'audio': 'student/history/Silkroad.m4a',
        'video': 'student/history/silkroad.mp4',
    },
    'tang-changan': {
        'audio': 'student/history/Tang.m4a',
        'video': 'student/history/Tang.mp4',
    },
    'song-innovation': {
        'audio': 'student/history/Song.m4a',
        'video': 'student/history/Song.mp4',
    },
    'zheng-he': {
        'audio': 'student/history/zhenghe.m4a',
        'video': 'student/history/Zhenghe.MP4',
    },
    'ming-qing-beijing': {
        'audio': 'student/history/forbidden-city-discovery-narration.m4a',
        'video': 'student/history/forbidden-city-1min.mp4',
    },
    'modern-and-taiwan': {
        'audio': 'student/history/modern-world-discovery-narration.m4a',
        'video': 'student/history/modern-world-1min.mp4',
    },
}


def media_for_lesson(slug):
    """Return a copy so views/templates cannot mutate the shared mapping."""
    return HISTORY_MEDIA.get(slug, {}).copy()
