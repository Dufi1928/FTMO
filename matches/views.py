from django.shortcuts import render
from rest_framework import viewsets
from .models import Match, MatchSet
from .serializers import MatchSerializer, MatchSetSerializer
from rest_framework.permissions import IsAuthenticatedOrReadOnly

class MatchViewSet(viewsets.ModelViewSet):
    queryset = Match.objects.all()
    serializer_class = MatchSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

class MatchSetViewSet(viewsets.ModelViewSet):
    queryset = MatchSet.objects.all()
    serializer_class = MatchSetSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
