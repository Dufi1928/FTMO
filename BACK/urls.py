from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView
from rest_framework.routers import DefaultRouter

# Importe tes ViewSets (teams, matches, etc.)
from teams.views import TeamViewSet, PlayerViewSet
from matches.views import MatchViewSet, MatchSetViewSet

router = DefaultRouter()
router.register(r'teams', TeamViewSet)
router.register(r'players', PlayerViewSet)
router.register(r'matches', MatchViewSet)
router.register(r'matchsets', MatchSetViewSet)

urlpatterns = [
    path('api/', include(router.urls)),

    # Schéma OpenAPI brut
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),

    # Interface Swagger
    path('api/schema/swagger-ui/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),

    # Interface ReDoc
    path('api/schema/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]
