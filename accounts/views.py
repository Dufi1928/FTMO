from django.shortcuts import render

from rest_framework import viewsets
from .models import User
from .serializers import UserSerializer, EmailTokenObtainPairSerializer
from rest_framework import generics, permissions
from .serializers import RegisterSerializer
from rest_framework_simplejwt.views import TokenObtainPairView

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

# accounts/views.py

class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]

class EmailTokenObtainPairView(TokenObtainPairView):
    serializer_class = EmailTokenObtainPairSerializer

