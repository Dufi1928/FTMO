from rest_framework.parsers import MultiPartParser, FormParser
from django.shortcuts import render
from rest_framework import viewsets
from .models import Team, Player
from .serializers import TeamSerializer, PlayerSerializer
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.permissions import AllowAny
from rest_framework.decorators import permission_classes


@permission_classes([AllowAny])
class TeamViewSet(viewsets.ModelViewSet):
    queryset         = Team.objects.all()
    serializer_class = TeamSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    parser_classes     = [MultiPartParser, FormParser]

class PlayerViewSet(viewsets.ModelViewSet):
    queryset = Player.objects.all()
    serializer_class = PlayerSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]





