from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView
from rest_framework.routers import DefaultRouter
from django.conf import settings
from django.conf.urls.static import static

# Importe tes ViewSets (teams, matches, etc.)
from teams.views import TeamViewSet, PlayerViewSet
from matches.views import MatchViewSet, MatchSetViewSet
from django.contrib import admin

router = DefaultRouter()
router.register(r'teams', TeamViewSet)
router.register(r'players', PlayerViewSet)
router.register(r'matches', MatchViewSet)
router.register(r'matchsets', MatchSetViewSet)

urlpatterns = [
    path('api/', include(router.urls)),

    path('api/auth/', include('auth.urls')),

    path('admin/', admin.site.urls),
    # Schéma OpenAPI brut
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),

    # Interface Swagger
    path('api/schema/swagger-ui/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),

    # Interface ReDoc
    path('api/schema/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)