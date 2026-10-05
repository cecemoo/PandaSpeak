from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db.models import Q

from .models import Vocabulary, Sentence, Idiom


@login_required(login_url='my_login')
def material_duplicate_search(request):
    """Search existing learning materials before a teacher/manager adds a new item."""
    material_type = (request.GET.get("type") or "").strip().lower()
    query = (request.GET.get("q") or "").strip()

    if len(query) < 1:
        return JsonResponse({"results": [], "exact": False})

    if material_type == "vocabulary":
        qs = Vocabulary.objects.filter(
            Q(word__icontains=query) |
            Q(pinyin__icontains=query) |
            Q(english_translation__icontains=query)
        ).order_by("word")[:10]
        results = [
            {
                "primary": item.word,
                "secondary": " · ".join(filter(None, [item.pinyin, item.english_translation])),
                "exact": item.word.strip().casefold() == query.casefold(),
            }
            for item in qs
        ]
    elif material_type == "sentence":
        qs = Sentence.objects.filter(text__icontains=query).order_by("text")[:10]
        results = [
            {
                "primary": item.text,
                "secondary": "Existing sentence",
                "exact": item.text.strip().casefold() == query.casefold(),
            }
            for item in qs
        ]
    elif material_type == "expression":
        qs = Idiom.objects.filter(
            Q(idiom__icontains=query) |
            Q(pinyin__icontains=query) |
            Q(english_translation__icontains=query)
        ).order_by("idiom")[:10]
        results = [
            {
                "primary": item.idiom,
                "secondary": " · ".join(filter(None, [item.pinyin, item.english_translation])),
                "exact": item.idiom.strip().casefold() == query.casefold(),
            }
            for item in qs
        ]
    else:
        return JsonResponse({"error": "Unknown material type."}, status=400)

    return JsonResponse({
        "results": results,
        "exact": any(item["exact"] for item in results),
    })
