
from rest_framework import viewsets, permissions,status,generics
from rest_framework.authentication import TokenAuthentication
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import User, Morphology
from .serializers import UserSerializer, MorphologySerializer,RegisterSerializer
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token



class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get_permissions(self):
        if self.action == 'list':
            return [permissions.IsAdminUser()]
        if self.action in ['update', 'partial_update', 'retrieve']:
            return [permissions.IsAuthenticated()]
        if self.action == 'destroy':
            return [permissions.IsAdminUser()]
        return super().get_permissions()


    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return User.objects.all()
        return User.objects.filter(id=user.id)

    @action(detail=False, methods=['GET', 'PATCH'], permission_classes=[permissions.IsAuthenticated])
    def me(self, request):
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)


class RegisterView(generics.CreateAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = RegisterSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data['email']
        password = serializer.validated_data['password']

        # Vérifier si un utilisateur avec cet email existe déjà
        if User.objects.filter(email=email).exists():
            return Response(
                {"error": "Un utilisateur avec cet email existe déjà."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Création de l'utilisateur
        user = User.objects.create_user(email=email, password=password)
        token, created = Token.objects.get_or_create(user=user)

        # Retourner uniquement le token et l'ID utilisateur
        data = {
            'token': token.key,
            'user_id': user.id,
        }
        headers = self.get_success_headers(data)
        return Response(data, status=status.HTTP_201_CREATED, headers=headers)


class MorphologyViewSet(viewsets.ModelViewSet):
    queryset = Morphology.objects.all()
    serializer_class = MorphologySerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Morphology.objects.all()
        return Morphology.objects.filter(user=user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class CustomAuthToken(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            'token': token.key,
            'user_id': user.id,
        })

obtain_auth_token = CustomAuthToken.as_view()
