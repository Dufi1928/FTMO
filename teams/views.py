from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated, AllowAny
from rest_framework.response import Response
from django.db.models import Prefetch

from .models import Team, Player, Schedule, AudienceCategory
from .serializers import TeamSerializer, PlayerSerializer, ScheduleSerializer,AudienceCategorySerializer


class TeamViewSet(viewsets.ModelViewSet):
    queryset = Team.objects.all()
    serializer_class = TeamSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get_queryset(self):
        return (
            Team.objects
            .all()
            .prefetch_related('players', 'schedules')
        )

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def my_team(self, request):
        logs = []

        user = request.user
        logs.append(f"Utilisateur authentifié : {getattr(user, 'email', '')} (ID: {user.id})")

        if not user.is_authenticated:
            logs.append("⚠️ Utilisateur non authentifié.")
            return Response({'detail': 'Non authentifié', 'logs': logs}, status=403)

        team = getattr(user, 'fkteam', None)
        if team:
            logs.append(f"✅ Équipe trouvée : ID {team.id}, nom = {team.club_name}")
            serializer = self.get_serializer(team)
            return Response({'team': serializer.data, 'logs': logs})
        else:
            logs.append("❌ Aucun fkteam lié à l'utilisateur.")
            return Response({'detail': 'Aucune équipe trouvée', 'logs': logs}, status=404)

    def get_queryset(self):
        return (
            Team.objects
            .all()
            .prefetch_related(
                'players',
                Prefetch('schedules', queryset=Schedule.objects.prefetch_related('categories'))
            )
        )

class AudienceCategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = AudienceCategory.objects.all().order_by('label')
    serializer_class = AudienceCategorySerializer
    permission_classes = [IsAuthenticatedOrReadOnly]


class PlayerViewSet(viewsets.ModelViewSet):
    queryset = Player.objects.all()
    serializer_class = PlayerSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def create(self, request, *args, **kwargs):
        data = request.data

        email = (data.get('email') or '').strip().lower()
        first_name = (data.get('first_name') or '').strip().lower()
        last_name = (data.get('last_name') or '').strip().lower()
        birth_date = data.get('birth_date')

        # Email unique
        if email and Player.objects.filter(email__iexact=email).exists():
            return Response(
                {'detail': 'Un joueur avec cet email existe déjà.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Unicité (nom + prénom + date de naissance)
        if Player.objects.filter(
            first_name__iexact=first_name,
            last_name__iexact=last_name,
            birth_date=birth_date
        ).exists():
            return Response(
                {'detail': 'Un joueur avec ce nom, prénom et date de naissance existe déjà.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

class ScheduleViewSet(viewsets.ModelViewSet):
    serializer_class = ScheduleSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        team = getattr(user, 'fkteam', None)
        qs = Schedule.objects.all().prefetch_related('categories')
        # Filtrer sur l’équipe de l’utilisateur (évite de voir/modifier les autres)
        if team:
            qs = qs.filter(team=team)
        return qs

    def perform_create(self, serializer):
        team = getattr(self.request.user, 'fkteam', None)
        if not team:
            raise PermissionDenied("Aucune équipe liée à cet utilisateur.")
        serializer.save(team=team)

    def perform_update(self, serializer):
        # Optionnel: s'assurer que l'objet appartient bien à l’équipe de l’utilisateur
        obj = self.get_object()
        team = getattr(self.request.user, 'fkteam', None)
        if not team or obj.team_id != team.id:
            raise PermissionDenied("Vous ne pouvez modifier que les créneaux de votre équipe.")
        serializer.save()
