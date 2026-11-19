"""Serves questions for the homepage 60-Second Chinese Challenge.

Each visitor (identified by a hash of their IP address) cycles through
the whole question bank before any word or idiom repeats: the endpoint
excludes the items most recently served to that visitor, picks the next
question at random from what is left, and records the serve.
"""
import hashlib
import random

from django.http import JsonResponse
from django.views.decorators.http import require_POST

from .challenge_data import CHALLENGE_ITEMS
from .models import ChallengeServe


def _ip_hash(request):
    forwarded = request.META.get('HTTP_X_FORWARDED_FOR', '')
    ip = forwarded.split(',')[0].strip() if forwarded else request.META.get('REMOTE_ADDR', '')
    return hashlib.sha256(ip.encode('utf-8')).hexdigest()


@require_POST
def challenge_next(request):
    ip_hash = _ip_hash(request)
    bank_size = len(CHALLENGE_ITEMS)
    recent = list(
        ChallengeServe.objects.filter(ip_hash=ip_hash)
        .order_by('-created_at', '-id')
        .values_list('item_text', flat=True)[:bank_size - 1]
    )
    seen = set(recent)
    candidates = [item for item in CHALLENGE_ITEMS if item['text'] not in seen]
    if not candidates:  # safety net; the window above should prevent this
        last = recent[0] if recent else None
        candidates = [item for item in CHALLENGE_ITEMS if item['text'] != last] or list(CHALLENGE_ITEMS)
    item = random.choice(candidates)
    ChallengeServe.objects.create(ip_hash=ip_hash, item_text=item['text'])
    pool = [other['answer'] for other in CHALLENGE_ITEMS
            if other['kind'] == item['kind'] and other['answer'] != item['answer']]
    choices = random.sample(pool, 3) + [item['answer']]
    random.shuffle(choices)
    return JsonResponse({
        'text': item['text'],
        'pinyin': item['pinyin'],
        'zhuyin': item['zhuyin'],
        'kind': item['kind'],
        'choices': choices,
        'answer': item['answer'],
    })
