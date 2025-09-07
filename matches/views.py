from rest_framework import viewsets, status, filters
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.views import APIView
from django.db.models import Sum, F, Q, IntegerField, Value, Case, When
from django.db.models.functions import Coalesce
import re
from typing import Optional

from .models import Match, MatchSet
from .serializers import MatchSerializer, MatchSetSerializer
from teams.models import Player

class MatchViewSet(viewsets.ModelViewSet):
    serializer_class = MatchSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        return (
            Match.objects
            .annotate(
                ann_total_points_home=Coalesce(Sum('match_sets__home_points'), 0),
                ann_total_points_away=Coalesce(Sum('match_sets__away_points'), 0),
            )
            .prefetch_related(
                'match_sets',
                'match_sets__home_players',
                'match_sets__away_players',
            )
        )

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def my_team(self, request):
        user = request.user
        logs = [f"Utilisateur : {user.email} (ID: {user.id})"]

        team = getattr(user, 'fkteam', None)
        if not team:
            logs.append("❌ Aucun fkteam trouvé pour cet utilisateur.")
            return Response({'detail': 'Aucune équipe trouvée', 'logs': logs}, status=404)

        logs.append(f"✅ Équipe trouvée : {team.club_name} (ID: {team.id})")

        matches = self.get_queryset().filter(Q(home_team=team) | Q(away_team=team)).order_by('-scheduled_datetime')
        logs.append(f"📦 {matches.count()} match(s) récupéré(s).")

        serializer = self.get_serializer(matches, many=True)
        return Response({'matches': serializer.data, 'logs': logs})



class MatchSetViewSet(viewsets.ModelViewSet):
    queryset = MatchSet.objects.all()
    serializer_class = MatchSetSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    search_fields = ['match']
    filter_backends = [filters.SearchFilter]

    def get_queryset(self):
        queryset = super().get_queryset()
        match_id = self.request.query_params.get('match')
        if match_id:
            queryset = queryset.filter(match_id=match_id)
        return queryset

    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated])
    def bulk_create(self, request):
        """
        Upsert par (match, match_identifier).
        Accepte home_players / away_players (listes d'IDs) ou home_player / away_player (IDs simples).
        """
        sets_data = request.data
        if not isinstance(sets_data, list):
            return Response({'detail': 'Une liste est attendue.'}, status=status.HTTP_400_BAD_REQUEST)

        updated_or_created = []

        for data in sets_data:
            match_id = data.get('match')
            match_identifier = data.get('match_identifier')
            if not match_id or not match_identifier:
                continue

            instance, _ = MatchSet.objects.update_or_create(
                match_id=match_id,
                match_identifier=match_identifier,
                defaults={
                    'set_type': data.get('set_type', 'single'),
                    'home_points': data.get('home_points', 0),
                    'away_points': data.get('away_points', 0),
                }
            )

            # M2M: accepte soit listes, soit single id
            hp = data.get('home_players')
            ap = data.get('away_players')
            if hp is None and data.get('home_player') is not None:
                hp = [data['home_player']]
            if ap is None and data.get('away_player') is not None:
                ap = [data['away_player']]

            if hp is not None:
                instance.home_players.set(hp)
            if ap is not None:
                instance.away_players.set(ap)

            updated_or_created.append(instance)

        serializer = self.get_serializer(updated_or_created, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class StatsView(APIView):
    """Retourne les points marqués et concédés par joueur pour une catégorie."""
    permission_classes = [IsAuthenticatedOrReadOnly]

    VALID_CATEGORIES = {
        "feminines",
        "masculins",
        "doubles-masculins",
        "doubles-masculin-feminin",
        "jeunes",
        "doubles-masculin-jeune",
        "doubles-feminin-jeune",
    }

    def _identify_category(self, match_identifier: str) -> Optional[str]:
        letters = re.findall(r"[A-Z]", match_identifier or "")
        if len(letters) == 2:
            if letters[0] == letters[1] == "F":
                return "feminines"
            if letters[0] == letters[1] == "M":
                return "masculins"
            if letters[0] == letters[1] == "J":
                return "jeunes"
        elif len(letters) == 3 and letters[0] == "D":
            combo = set(letters[1:])
            if combo == {"M"}:
                return "doubles-masculins"
            if combo == {"M", "F"}:
                return "doubles-masculin-feminin"
            if combo == {"M", "J"}:
                return "doubles-masculin-jeune"
            if combo == {"F", "J"}:
                return "doubles-feminin-jeune"
        return None

    def get(self, request, category: str):
        category = category.replace("_", "-").lower()
        if category not in self.VALID_CATEGORIES:
            return Response({"detail": "Catégorie inconnue"}, status=404)

        stats = {}
        match_sets = MatchSet.objects.prefetch_related("home_players", "away_players").all()
        for ms in match_sets:
            if self._identify_category(ms.match_identifier) != category:
                continue
            for player in ms.home_players.all():
                data = stats.setdefault(player.id, {"player": player, "points_scored": 0, "points_conceded": 0})
                data["points_scored"] += ms.home_points
                data["points_conceded"] += ms.away_points
            for player in ms.away_players.all():
                data = stats.setdefault(player.id, {"player": player, "points_scored": 0, "points_conceded": 0})
                data["points_scored"] += ms.away_points
                data["points_conceded"] += ms.home_points

        results = [
            {
                "player_id": pid,
                "first_name": data["player"].first_name,
                "last_name": data["player"].last_name,
                "points_scored": data["points_scored"],
                "points_conceded": data["points_conceded"],
            }
            for pid, data in stats.items()
        ]

        return Response({"category": category, "results": results})
