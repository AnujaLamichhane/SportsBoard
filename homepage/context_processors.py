from organizer.models import Event,Match


def sports_menu(request):
    # Get unique sports from main Events
    event_sports = set(Event.objects.values_list('game_type', flat=True))
    # Get unique sports from individual Matches
    match_sports = set(Match.objects.values_list('game_type', flat=True))
    all_codes = event_sports | match_sports
    # Combine them and remove 'MULTI' (Sports Week) from being a direct filter link
    formatted_sports = []
    for code in sorted(all_codes):
        if code and code != 'MULTI':  # Skip 'Multi-sport' as a dropdown option
            formatted_sports.append({
                'code': code,
                'name': code.lower().capitalize()  # Converts 'CRICKET' to 'Cricket'
            })

    return {
        'nav_sports': formatted_sports
    }