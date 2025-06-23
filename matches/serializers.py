from rest_framework import serializers
from .models import Match, MatchSet

class MatchSerializer(serializers.ModelSerializer):
    home_team_name = serializers.CharField(source='home_team.club_name', read_only=True)
    away_team_name = serializers.CharField(source='away_team.club_name', read_only=True)
    home_team_logo = serializers.CharField(source='home_team.image', read_only=True)
    away_team_logo = serializers.CharField(source='away_team.image', read_only=True)
    is_home_team = serializers.SerializerMethodField()

    class Meta:
        model = Match
        fields = [
            'id',
            'home_team',
            'home_team_name',
            'home_team_logo',
            'away_team',
            'away_team_name',
            'away_team_logo',
            'scheduled_datetime',
            'status',
            'global_score_home',
            'global_score_away',
            'created_at',
            'validation_status_home',
            'validation_status_away',
            'validation_status_superadmin',
            'is_home_team'
        ]

    def get_is_home_team(self, obj):
        user = self.context.get('request').user
        user_team = getattr(user, 'fkteam', None)
        return obj.home_team == user_team

class MatchSetSerializer(serializers.ModelSerializer):
    class Meta:
        model = MatchSet
        fields = [
            'id',
            'match',
            'set_type',
            'match_identifier',
            'home_player',
            'away_player',
            'home_points',
            'away_points'
        ]
