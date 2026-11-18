"""Public "Get Help" assistant for PandaSpeak.

Powers the bottom-right help bubble shown across the site. The assistant
answers common questions about PandaSpeak and guides visitors toward
registering, subscribing, and adding the Plus plan. It is available to
anonymous visitors (its main audience) as well as signed-in users, so it is
rate-limited per IP and every input is length-capped.
"""
import json
import logging
import os

import requests
from opencc import OpenCC
from django.core.cache import cache
from django.http import JsonResponse
from django.views.decorators.http import require_POST

logger = logging.getLogger(__name__)

TRADITIONAL_CONVERTER = OpenCC('s2twp')
STANDARD_MANDARIN_REPLACEMENTS = {'喫': '吃', '哪兒': '哪裡', '這兒': '這裡', '那兒': '那裡'}

MAX_MESSAGE_CHARS = 600
MAX_HISTORY_ITEMS = 8
MAX_HISTORY_CHARS = 600
RATE_LIMIT_PER_HOUR = 30

FALLBACK_REPLY = (
    "Sorry, I'm having trouble answering right now. You can browse our "
    "[learning page](/learn-traditional-chinese-online/) for an overview, "
    "[create a free account](/register/) to get started, or email us at "
    "pandaspeaksupport@gmail.com and a person will help you."
)

SYSTEM_PROMPT = """You are the PandaSpeak virtual assistant, a friendly helper on pandaspeak.org. PandaSpeak teaches Traditional Chinese to adult learners worldwide, online, with learning materials available 24/7.

Your job: answer questions briefly and guide the visitor to the next step — creating a free account, subscribing, or adding the Plus plan. Many visitors don't want to read the whole website, so be their shortcut.

WHAT PANDASPEAK OFFERS
- Three levels: Level 1 (beginner), Level 2 (intermediate), Level 3 (advanced). Level 1 focuses on vocabulary and pronunciation; Levels 2-3 build on that and add general Chinese culture.
- Learning materials: vocabulary, sentences, and Chinese expressions/idioms, all with BoPoMoFo (Zhuyin) and Pinyin pronunciation support.
- Student dashboard features: Chinese bingo (including Create Your Own Bingo), flashcards, challenge games, AI conversation practice, assessment tests, and Cultural Insights lessons.
- The Chinese history section: short animated history lessons with English subtitles.
- Online tutoring with teachers (booked separately, paid per session): [Tutoring](/course/).
- Free resources: a [free BoPoMoFo chart](/free-bopomofo-chart/) and a [free Chinese idioms PDF](/free-chinese-idioms/).

PRICING (state exactly like this, never change the numbers)
- Base subscription: $15/year. It is required to access the learning materials.
- Plus plan: a $4.99/month upgrade on top of the base subscription. It covers up to 50 AI conversations per month and the Chinese history section. Plus is never sold on its own — the base subscription comes first.
- Tutoring is priced per session on the tutoring page.

HOW TO GET STARTED (give these steps when asked)
1. [Create a free account](/register/) and verify your email.
2. [Subscribe to the base plan](/subscription/subscribe/) ($15/year) to unlock the learning materials.
3. Optionally [add the Plus plan](/subscription/stripe/upgrade-plus/) ($4.99/month) for AI conversation practice and the history section.
Signed-in users can also reach everything from their dashboard.

RULES
- Keep answers short: usually 2-4 sentences. Use a link (markdown format, site-relative paths exactly as given above) whenever a page would help.
- Answer in the language the visitor writes in. Any Chinese you write must be Traditional Chinese characters with BoPoMoFo and Pinyin when you give pronunciations.
- Only discuss PandaSpeak and learning Chinese. If asked about something unrelated, politely steer back.
- Never invent prices, features, discounts, or policies that are not listed above. There are no free trials or complimentary accounts; the free BoPoMoFo chart and idioms PDF are the free resources.
- For account-specific problems (billing, login trouble, a payment question), don't guess: point them to [Contact](/contact/) or pandaspeaksupport@gmail.com.
- Never claim to be a human. If asked, say you are PandaSpeak's virtual assistant.
"""


def _traditional(text):
    value = TRADITIONAL_CONVERTER.convert(str(text or ''))
    for source, target in STANDARD_MANDARIN_REPLACEMENTS.items():
        value = value.replace(source, target)
    return value


def _client_ip(request):
    forwarded = request.META.get('HTTP_X_FORWARDED_FOR', '')
    if forwarded:
        return forwarded.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR', 'unknown')


def _rate_limited(request):
    key = 'help_chat_rl:%s' % _client_ip(request)
    count = cache.get(key, 0)
    if count >= RATE_LIMIT_PER_HOUR:
        return True
    cache.set(key, count + 1, 3600)
    return False


def _call_openai(messages):
    api_key = os.getenv('OPENAI_API_KEY', '')
    if not api_key:
        raise RuntimeError('OPENAI_API_KEY is not configured on the server.')
    model = os.getenv('OPENAI_HELP_CHAT_MODEL') or os.getenv('OPENAI_AI_CONVERSATION_MODEL', 'gpt-5.6-luna')
    payload = {'model': model, 'input': [{'role': 'system', 'content': SYSTEM_PROMPT}] + messages,
               'max_output_tokens': 400}
    response = requests.post('https://api.openai.com/v1/responses',
                             headers={'Authorization': 'Bearer %s' % api_key,
                                      'Content-Type': 'application/json'},
                             json=payload, timeout=30)
    response.raise_for_status()
    data = response.json()
    text = data.get('output_text', '').strip()
    if not text:
        parts = []
        for item in data.get('output', []):
            for content in item.get('content', []):
                if content.get('type') == 'output_text' and content.get('text'):
                    parts.append(content['text'])
        text = '\n'.join(parts).strip()
    if not text:
        raise RuntimeError('The AI service returned an empty response.')
    return _traditional(text)


@require_POST
def help_chat(request):
    try:
        body = json.loads(request.body.decode('utf-8'))
    except (json.JSONDecodeError, UnicodeDecodeError):
        return JsonResponse({'error': 'Invalid request.'}, status=400)

    message = str(body.get('message', '')).strip()[:MAX_MESSAGE_CHARS]
    if not message:
        return JsonResponse({'error': 'Please type a question.'}, status=400)

    if _rate_limited(request):
        return JsonResponse({'reply': "You've asked a lot of questions in the last hour — "
                                        'please try again a little later, or email us at '
                                        'pandaspeaksupport@gmail.com and a person will help you.'})

    messages = []
    history = body.get('history')
    if isinstance(history, list):
        for item in history[-MAX_HISTORY_ITEMS:]:
            if not isinstance(item, dict):
                continue
            role = item.get('role')
            content = str(item.get('content', '')).strip()[:MAX_HISTORY_CHARS]
            if role in ('user', 'assistant') and content:
                messages.append({'role': role, 'content': content})
    if request.user.is_authenticated:
        messages.append({'role': 'system',
                         'content': 'Note: this visitor is already signed in to PandaSpeak. '
                                    'Do not push them to register; help them with their account, '
                                    'subscription, Plus plan, or finding features in their dashboard.'})
    messages.append({'role': 'user', 'content': message})

    try:
        reply = _call_openai(messages)
    except Exception:
        logger.exception('help_chat: AI call failed')
        return JsonResponse({'reply': FALLBACK_REPLY})
    return JsonResponse({'reply': reply})
