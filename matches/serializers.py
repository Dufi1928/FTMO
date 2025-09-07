from rest_framework import serializers
from .models import Match, MatchSet
from teams.models import Player  # Assure-toi d'importer Player


class MatchSetBriefSerializer(serializers.ModelSerializer):
    home_players = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    away_players = serializers.PrimaryKeyRelatedField(many=True, read_only=True)

    class Meta:
        model = MatchSet
        fields = [
            'id', 'set_type', 'match_identifier',
            'home_points', 'away_points',
            'home_players', 'away_players',
        ]

class MatchSerializer(serializers.ModelSerializer):
    home_team_name = serializers.CharField(source='home_team.club_name', read_only=True)
    away_team_name = serializers.CharField(source='away_team.club_name', read_only=True)
    home_team_logo = serializers.CharField(source='home_team.image', read_only=True)
    away_team_logo = serializers.CharField(source='away_team.image', read_only=True)
    is_home_team = serializers.SerializerMethodField()

    # ← mappe sur les annotations de la queryset
    total_points_home = serializers.IntegerField(source='ann_total_points_home', read_only=True)
    total_points_away = serializers.IntegerField(source='ann_total_points_away', read_only=True)

    sets = serializers.SerializerMethodField()

    class Meta:
        model = Match
        fields = [
            'id',
            'home_team', 'home_team_name', 'home_team_logo',
            'away_team', 'away_team_name', 'away_team_logo',
            'scheduled_datetime', 'status', 'created_at',
            'validation_status_home', 'validation_status_away', 'validation_status_superadmin',
            'is_home_team',
            'total_points_home', 'total_points_away',
            'sets',
        ]

    def get_is_home_team(self, obj):
        user = self.context.get('request').user
        user_team = getattr(user, 'fkteam', None)
        return obj.home_team == user_team

    def get_sets(self, obj):
        qs = obj.match_sets.all().order_by('set_type', 'match_identifier', 'id')
        return MatchSetBriefSerializer(qs, many=True).data


class MatchSetSerializer(serializers.ModelSerializer):
    # ⬇️ Retourne/reçoit des listes d'IDs joueurs
    home_players = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Player.objects.all(), required=False
    )
    away_players = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Player.objects.all(), required=False
    )

    class Meta:
        model = MatchSet
        fields = [
            'id',
            'match',
            'set_type',
            'match_identifier',
            'home_players',
            'away_players',
            'home_points',
            'away_points',
            'created_at',
        ]
        read_only_fields = ['created_at']

    def validate(self, attrs):
        set_type = attrs.get('set_type') or (self.instance.set_type if self.instance else None)
        hp = attrs.get('home_players', None)
        ap = attrs.get('away_players', None)

        # Valide la cardinalité (1 pour single, 2 pour double)
        if set_type == 'double':
            if hp is not None and len(hp) not in (0, 2):
                raise serializers.ValidationError('home_players doit contenir exactement 2 IDs pour un double.')
            if ap is not None and len(ap) not in (0, 2):
                raise serializers.ValidationError('away_players doit contenir exactement 2 IDs pour un double.')
        elif set_type == 'single':
            if hp is not None and len(hp) not in (0, 1):
                raise serializers.ValidationError('home_players doit contenir exactement 1 ID pour un simple.')
            if ap is not None and len(ap) not in (0, 1):
                raise serializers.ValidationError('away_players doit contenir exactement 1 ID pour un simple.')

        return attrs

    def create(self, validated_data):
        home_players = validated_data.pop('home_players', [])
        away_players = validated_data.pop('away_players', [])
        instance = MatchSet.objects.create(**validated_data)
        if home_players:
            instance.home_players.set(home_players)
        if away_players:
            instance.away_players.set(away_players)
        return instance

    def update(self, instance, validated_data):
        home_players = validated_data.pop('home_players', None)
        away_players = validated_data.pop('away_players', None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if home_players is not None:
            instance.home_players.set(home_players)
        if away_players is not None:
            instance.away_players.set(away_players)

        return instance
