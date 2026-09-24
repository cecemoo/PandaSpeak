from django import template

from student.models import LearnedItem

register = template.Library()


@register.inclusion_tag('student/_recently_learned_modals.html', takes_context=True)
def recently_learned_modals(context):
    request = context.get('request')
    user = getattr(request, 'user', None)
    if not user or not user.is_authenticated:
        return {'recently_learned': []}

    items = LearnedItem.objects.filter(student=user).select_related(
        'vocabulary', 'sentence', 'idiom'
    ).order_by('-learned_at')[:5]

    return {'recently_learned': items}
