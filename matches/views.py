from django.shortcuts import render
from rest_framework import viewsets
from .models import Match, MatchSet
from .serializers import MatchSerializer, MatchSetSerializer
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from rest_framework.response import Response
from django.db.models import Q
from rest_framework.decorators import action
from rest_framework import status
from rest_framework import filters


class MatchViewSet(viewsets.ModelViewSet):
    queryset = Match.objects.all()
    serializer_class = MatchSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]


    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def my_team(self, request):
        user = request.user
        logs = [f"Utilisateur : {user.email} (ID: {user.id})"]

        team = getattr(user, 'fkteam', None)
        if not team:
            logs.append("❌ Aucun fkteam trouvé pour cet utilisateur.")
            return Response({'detail': 'Aucune équipe trouvée', 'logs': logs}, status=404)

        logs.append(f"✅ Équipe trouvée : {team.club_name} (ID: {team.id})")

        # Matchs où l'équipe est soit à domicile, soit à l'extérieur
        matches = Match.objects.filter(Q(home_team=team) | Q(away_team=team)).order_by('-scheduled_datetime')
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
        sets_data = request.data

        if not isinstance(sets_data, list):
            return Response({'detail': 'Une liste est attendue.'}, status=status.HTTP_400_BAD_REQUEST)

        updated_or_created = []

        for set_data in sets_data:
            match = set_data.get('match')
            match_identifier = set_data.get('match_identifier')

            if not match or not match_identifier:
                continue  # Ignore les sets incomplets

            instance, created = MatchSet.objects.update_or_create(
                match_id=match,
                match_identifier=match_identifier,
                defaults={
                    'set_type': set_data.get('set_type', 'simple'),
                    'home_player_id': set_data.get('home_player'),
                    'away_player_id': set_data.get('away_player'),
                    'home_points': set_data.get('home_points', 0),
                    'away_points': set_data.get('away_points', 0),
                }
            )
            updated_or_created.append(instance)

        serializer = self.get_serializer(updated_or_created, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
