from rest_framework import viewsets, status, filters
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import action
from django.db.models import Sum, F, Q, IntegerField, Value, Case, When
from django.db.models.functions import Coalesce

from .models import Match, MatchSet
from .serializers import MatchSerializer, MatchSetSerializer

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
