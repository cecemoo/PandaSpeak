from django import template


register = template.Library()

@register.filter
def provider_display_name(user):
    if not user:
        return
    provider = getattr(user, "provider", None)
    if provider and getattr(provider, "display_name", None):
        return provider.display_name
    full = ""
    try:
        full = user.get_full_name()
    except Exception:
        full = ""
    return full or getattr(user, "username", "") or str(user)