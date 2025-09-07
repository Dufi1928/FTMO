from django.http import JsonResponse, Http404
from .models import PlayerStat


def category_stats(request, category: str):
    """Return stats for a given category.

    For double categories (those whose name starts with ``DOUBLES``) players are
    returned as pairs formatted as "player1 / player2" so that the frontend can
    display the team as a single entry.
    """

    stats = PlayerStat.objects.filter(category=category)

    if category.upper().startswith("DOUBLES"):
        # Pair players sequentially: each pair represents one team.
        iterator = iter(stats)
        data = []
        for stat in iterator:
            try:
                partner = next(iterator)
            except StopIteration:
                # Odd number of players; return the remaining player alone.
                players = stat.player.name
            else:
                players = f"{stat.player.name} / {partner.player.name}"

            data.append(
                {
                    "player": players,
                    "sets_won": stat.sets_won,
                    "sets_lost": stat.sets_lost,
                }
            )
    else:
        data = [
            {
                "player": stat.player.name,
                "sets_won": stat.sets_won,
                "sets_lost": stat.sets_lost,
            }
            for stat in stats
        ]

    return JsonResponse({"category": category, "stats": data})


def player_category_stats(request, category: str, player_id: int):
    """Return stats for a specific player and category.

    For double categories the partner is looked up and both names are returned
    joined with a slash.
    """

    try:
        stat = PlayerStat.objects.get(category=category, player_id=player_id)
    except PlayerStat.DoesNotExist as exc:
        raise Http404("Stat not found") from exc

    if category.upper().startswith("DOUBLES"):
        partners = PlayerStat.objects.filter(
            category=category,
            sets_won=stat.sets_won,
            sets_lost=stat.sets_lost,
        ).exclude(player_id=player_id)
        player_name = " / ".join([stat.player.name] + [p.player.name for p in partners])
    else:
        player_name = stat.player.name

    data = {
        "player": player_name,
        "category": category,
        "sets_won": stat.sets_won,
        "sets_lost": stat.sets_lost,
    }
    return JsonResponse(data)
