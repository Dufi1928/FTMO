from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework import viewsets
from .models import Team, Player, Schedule
from .serializers import TeamSerializer, PlayerSerializer
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.permissions import AllowAny
from rest_framework.decorators import permission_classes
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated


@permission_classes([AllowAny])
class TeamViewSet(viewsets.ModelViewSet):
    queryset         = Team.objects.all()
    serializer_class = TeamSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    parser_classes     = [MultiPartParser, FormParser]

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def my_team(self, request):
        logs = []  # Liste des messages à retourner

        user = request.user
        logs.append(f"Utilisateur authentifié : {user.email} (ID: {user.id})")

        if not user.is_authenticated:
            logs.append("⚠️ Utilisateur non authentifié.")
            return Response({'detail': 'Non authentifié', 'logs': logs}, status=403)

        if user.fkteam:
            logs.append(f"✅ Équipe trouvée : ID {user.fkteam.id}, nom = {user.fkteam.club_name}")
            team = user.fkteam
            serializer = self.get_serializer(team)
            return Response({'team': serializer.data, 'logs': logs})
        else:
            logs.append("❌ Aucun fkteam lié à l'utilisateur.")
            return Response({'detail': 'Aucune équipe trouvée', 'logs': logs}, status=404)

class PlayerViewSet(viewsets.ModelViewSet):
    queryset = Player.objects.all()
    serializer_class = PlayerSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def create(self, request, *args, **kwargs):
        data = request.data

        email = data.get('email', '').strip().lower()
        first_name = data.get('first_name', '').strip().lower()
        last_name = data.get('last_name', '').strip().lower()
        birth_date = data.get('birth_date')

        # Vérifier email unique (insensible à la casse)
        if email and Player.objects.filter(email__iexact=email).exists():
            return Response({'detail': 'Un joueur avec cet email existe déjà.'}, status=400)

        # Vérifier unicité nom + prénom + date de naissance
        if Player.objects.filter(
            first_name__iexact=first_name,
            last_name__iexact=last_name,
            birth_date=birth_date
        ).exists():
            return Response({'detail': 'Un joueur avec ce nom, prénom et date de naissance existe déjà.'}, status=400)

        return super().create(request, *args, **kwargs)







