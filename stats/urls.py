from django.urls import path
from . import views

urlpatterns = [
    path('<str:category>/', views.category_stats, name='category-stats'),
    path('<str:category>/player/<int:player_id>/', views.player_category_stats, name='player-category-stats'),
]
