from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from .places_data import PHOTO_CREDITS, SPOTS


@login_required
def famous_places(request):
    """Famous Spots & Food Map — open to every learning level."""
    return render(request, 'student/famous_places.html', {
        'spots': SPOTS,
        'photo_credits': PHOTO_CREDITS,
    })
