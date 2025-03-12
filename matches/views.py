from django.shortcuts import render
from rest_framework import viewsets
from .models import Match, MatchSet
from .serializers import MatchSerializer, MatchSetSerializer

class MatchViewSet(viewsets.ModelViewSet):
    queryset = Match.objects.all()
    serializer_class = MatchSerializer

class MatchSetViewSet(viewsets.ModelViewSet):
    queryset = MatchSet.objects.all()
    serializer_class = MatchSetSerializer
