from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView
from rest_framework.routers import DefaultRouter
from django.conf import settings
from django.conf.urls.static import static
from rest_framework_simplejwt.views import TokenRefreshView
from django.contrib import admin

from accounts.views import RegisterView, EmailTokenObtainPairView
from teams.views import TeamViewSet, PlayerViewSet, ScheduleViewSet, AudienceCategoryViewSet
from matches.views import MatchViewSet, MatchSetViewSet

# ==== ROUTER ====
router = DefaultRouter()
router.register(r'teams', TeamViewSet, basename='team')
router.register(r'players', PlayerViewSet, basename='player')
router.register(r'schedules', ScheduleViewSet, basename='schedule')
router.register(r'audience-categories', AudienceCategoryViewSet, basename='audiencecategory')
router.register(r'matches', MatchViewSet, basename='match')
router.register(r'matchsets', MatchSetViewSet, basename='matchset')

# ==== URLPATTERNS ====
urlpatterns = [
    path('api/register/', RegisterView.as_view(), name='register'),
    path('api/token/', EmailTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/', include(router.urls)),

    path('admin/', admin.site.urls),

    # Schéma OpenAPI
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/schema/swagger-ui/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/schema/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
