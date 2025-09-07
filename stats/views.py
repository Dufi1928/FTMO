from django.http import JsonResponse, Http404
from .models import PlayerStat


def category_stats(request, category: str):
    stats = PlayerStat.objects.filter(category=category)
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
    try:
        stat = PlayerStat.objects.get(category=category, player_id=player_id)
    except PlayerStat.DoesNotExist as exc:
        raise Http404("Stat not found") from exc
    data = {
        "player": stat.player.name,
        "category": category,
        "sets_won": stat.sets_won,
        "sets_lost": stat.sets_lost,
    }
    return JsonResponse(data)
