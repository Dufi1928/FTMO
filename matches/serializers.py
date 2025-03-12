from rest_framework import serializers
from .models import Match, MatchSet

class MatchSerializer(serializers.ModelSerializer):
    class Meta:
        model = Match
        fields = [
            'id', 'home_team', 'away_team', 'scheduled_datetime', 'status',
            'global_score_home', 'global_score_away', 'created_at',
            'validation_status_home', 'validation_status_away', 'validation_status_superadmin'
        ]

class MatchSetSerializer(serializers.ModelSerializer):
    class Meta:
        model = MatchSet
        fields = [
            'id', 'match', 'set_type', 'home_player', 'away_player',
            'status', 'home_points', 'away_points', 'created_at'
        ]
