from django.shortcuts import render
from rest_framework import viewsets
from .models import Team, Player
from .serializers import TeamSerializer, PlayerSerializer
from rest_framework.permissions import IsAuthenticatedOrReadOnly

class TeamViewSet(viewsets.ModelViewSet):
    queryset = Team.objects.all()
    serializer_class = TeamSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

class PlayerViewSet(viewsets.ModelViewSet):
    queryset = Player.objects.all()
    serializer_class = PlayerSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

