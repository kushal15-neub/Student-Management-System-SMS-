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
