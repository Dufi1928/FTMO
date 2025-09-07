from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated, AllowAny
from rest_framework.response import Response
from django.db.models import Prefetch, Q
from datetime import date
from matches.models import MatchSet

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

    @action(detail=True, methods=['get'])
    def stats(self, request, pk=None):
        player = self.get_object()

        categories = [
            'FEMININES', 'MASCULINS', 'DOUBLES MASCULINS',
            'DOUBLES MASCULIN-FEMININ', 'JEUNES',
            'DOUBLES MASCULIN-JEUNE', 'DOUBLES FEMININ-JEUNE',
        ]
        stats = {cat: {'won': 0, 'lost': 0} for cat in categories}

        sets_qs = MatchSet.objects.filter(
            Q(home_players=player) | Q(away_players=player)
        ).prefetch_related('home_players', 'away_players')

        for match_set in sets_qs:
            category = self._determine_category(match_set, player)
            if not category:
                continue
            won = (
                (match_set.home_points > match_set.away_points and player in match_set.home_players.all())
                or (match_set.away_points > match_set.home_points and player in match_set.away_players.all())
            )
            if won:
                stats[category]['won'] += 1
            else:
                stats[category]['lost'] += 1

        return Response({'player': player.id, 'stats': stats})

    def _determine_category(self, match_set, player):
        def is_female(p):
            civ = (p.civility or '').lower()
            return civ in ['mme', 'mlle', 'madame', 'mademoiselle']

        def is_young(p):
            if not p.birth_date:
                return False
            today = date.today()
            age = today.year - p.birth_date.year - (
                (today.month, today.day) < (p.birth_date.month, p.birth_date.day)
            )
            return age < 18

        if match_set.set_type == 'single':
            if is_young(player):
                return 'JEUNES'
            return 'FEMININES' if is_female(player) else 'MASCULINS'

        pair = (
            match_set.home_players.all()
            if player in match_set.home_players.all()
            else match_set.away_players.all()
        )
        genders = [is_female(p) for p in pair]
        ages = [is_young(p) for p in pair]

        if not any(genders) and not any(ages):
            return 'DOUBLES MASCULINS'
        if any(genders) and not any(ages):
            return 'DOUBLES MASCULIN-FEMININ'
        if not any(genders) and any(ages):
            return 'DOUBLES MASCULIN-JEUNE'
        if any(genders) and any(ages):
            return 'DOUBLES FEMININ-JEUNE'
        return None

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
