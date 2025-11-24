def display_name(request):
    """Provide a friendly display name for templates.

    Preference order:
    - If authenticated: first_name
    - Else full name
    - Else username
    - Else 'Guest'
    """
    user = getattr(request, "user", None)
    name = "Guest"
    if user and user.is_authenticated:
        first = getattr(user, "first_name", "") or ""
        full = ""
        try:
            full = user.get_full_name()
        except Exception:
            full = ""
        username = getattr(user, "username", "") or ""
        if first:
            name = first
        elif full:
            name = full
        elif username:
            name = username
    return {"display_name": name}


def social_providers_available(request):
    """Expose whether Google social login is configured for the current site.

    This prevents templates from calling allauth template tags that expect
    a configured SocialApp and causing a 500 when the SocialApp is missing.
    """
    try:
        from django.contrib.sites.shortcuts import get_current_site
        from allauth.socialaccount.models import SocialApp

        site = get_current_site(request)
        google_available = SocialApp.objects.filter(
            provider="google", sites=site
        ).exists()
    except Exception:
        google_available = False

    return {"social_google_available": google_available}
