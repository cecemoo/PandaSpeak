import random

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse

from subscription.decorators import subscription_required
from teacher.models import Tone


@login_required(login_url='my_login')
@subscription_required
def next_tone_base(request):
    """Return a complete four-tone set using a base different from the current one."""
    current_base = (request.GET.get('current') or '').strip()
    bases = list(
        Tone.objects.values_list('base_pinyin', flat=True)
        .exclude(base_pinyin='')
        .distinct()
        .order_by('base_pinyin')
    )
    alternatives = [base for base in bases if base != current_base]
    if alternatives:
        base = random.choice(alternatives)
    elif bases:
        base = bases[0]
    else:
        return JsonResponse({'error': 'No tone sets are available.'}, status=404)

    tones = Tone.objects.filter(base_pinyin=base).order_by('id')[:4]
    data = []
    for tone in tones:
        data.append({
            'tone_name': tone.tone_name,
            'symbol': tone.symbol,
            'example': tone.example,
            'description': tone.description,
            'audio_url': tone.audio_file.url if tone.audio_file else '',
        })

    if len(data) < 4:
        return JsonResponse({'error': 'This tone set is incomplete.'}, status=409)
    return JsonResponse({'base_pinyin': base, 'tones': data})
