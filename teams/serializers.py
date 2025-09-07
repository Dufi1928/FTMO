from decimal import Decimal

from django.db.models import Q, F, Sum, Case, When, IntegerField, Value
from django.db.models.functions import Coalesce
from rest_framework import serializers

from .models import Team, Player, Schedule, AudienceCategory
from matches.models import Match


# ---- Audience categories ----
class AudienceCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = AudienceCategory
        fields = ['id', 'code', 'label']


# ---- Players ----
class PlayerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Player
        fields = [
            'id', 'team', 'first_name', 'last_name',
            'civility', 'email', 'birth_date', 'profile_image'
        ]


# ---- Schedules (REMPLACE audience_type par categories/category_ids) ----
class ScheduleSerializer(serializers.ModelSerializer):
    categories = AudienceCategorySerializer(many=True, read_only=True)
    category_ids = serializers.PrimaryKeyRelatedField(
        many=True,
        source='categories',
        queryset=AudienceCategory.objects.all(),
        write_only=True,
        required=False
    )
    team = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Schedule
        fields = ['id', 'weekday', 'start_time', 'end_time', 'categories', 'category_ids', 'team']


# ---- Teams + stats ----
class TeamSerializer(serializers.ModelSerializer):
    # bornes explicites pour éviter les warnings DRF
    latitude = serializers.DecimalField(
        max_digits=9, decimal_places=6,
        min_value=Decimal('-90'), max_value=Decimal('90'),
        required=False, allow_null=True
    )
    longitude = serializers.DecimalField(
        max_digits=9, decimal_places=6,
        min_value=Decimal('-180'), max_value=Decimal('180'),
        required=False, allow_null=True
    )
    altitude_m = serializers.DecimalField(
        max_digits=7, decimal_places=1,
        required=False, allow_null=True
    )

    players = PlayerSerializer(many=True, read_only=True)
    schedules = ScheduleSerializer(many=True, read_only=True)

    # Stats
    matches_played = serializers.SerializerMethodField()
    matches_won = serializers.SerializerMethodField()
    matches_lost = serializers.SerializerMethodField()
    matches_drawn = serializers.SerializerMethodField()
    total_points_scored = serializers.SerializerMethodField()
    total_points_conceded = serializers.SerializerMethodField()

    class Meta:
        model = Team
        fields = [
            'id', 'club_name', 'club_short_description',
            'club_description_paragraph_1', 'club_description_paragraph_2',
            'latitude', 'longitude', 'altitude_m',
            'image', 'image_large', 'team_admin', 'email', 'updated_at',
            'players', 'schedules',
            'matches_played', 'matches_won', 'matches_lost',
            'matches_drawn', 'total_points_scored', 'total_points_conceded',
        ]

    # --- Helpers internes ---
    def _played_qs(self, team: Team):
        """
        Matchs de l'équipe (domicile ou extérieur), hors 'scheduled',
        annotés avec score_home / score_away calculés depuis les MatchSet.
        1 point par set gagné (single/double = même poids). Si tu veux
        pondérer les doubles, adapte les Case(...) ci-dessous.
        """
        win_home = Case(
            When(match_sets__home_points__gt=F('match_sets__away_points'), then=Value(1)),
            default=Value(0),
            output_field=IntegerField(),
        )
        win_away = Case(
            When(match_sets__away_points__gt=F('match_sets__home_points'), then=Value(1)),
            default=Value(0),
            output_field=IntegerField(),
        )

        return (
            Match.objects
            .filter(Q(home_team=team) | Q(away_team=team))
            .exclude(status='scheduled')
            .annotate(
                score_home=Coalesce(Sum(win_home), 0),
                score_away=Coalesce(Sum(win_away), 0),
            )
        )

    # --- Champs calculés ---
    def get_matches_played(self, obj: Team) -> int:
        return self._played_qs(obj).count()

    def get_matches_won(self, obj: Team) -> int:
        qs = self._played_qs(obj)
        return qs.filter(
            Q(home_team=obj, score_home__gt=F('score_away')) |
            Q(away_team=obj, score_away__gt=F('score_home'))
        ).count()

    def get_matches_lost(self, obj: Team) -> int:
        qs = self._played_qs(obj)
        return qs.filter(
            Q(home_team=obj, score_home__lt=F('score_away')) |
            Q(away_team=obj, score_away__lt=F('score_home'))
        ).count()

    def get_matches_drawn(self, obj: Team) -> int:
        qs = self._played_qs(obj)
        return qs.filter(score_home=F('score_away')).count()

    def get_total_points_scored(self, obj: Team) -> int:
        """
        Somme des sets gagnés par l'équipe (tous matchs joués).
        """
        qs = self._played_qs(obj)
        agg = qs.aggregate(
            home_scored=Coalesce(Sum(
                Case(When(home_team=obj, then=F('score_home')), default=Value(0), output_field=IntegerField())
            ), 0),
            away_scored=Coalesce(Sum(
                Case(When(away_team=obj, then=F('score_away')), default=Value(0), output_field=IntegerField())
            ), 0),
        )
        return int(agg['home_scored'] + agg['away_scored'])

    def get_total_points_conceded(self, obj: Team) -> int:
        """
        Somme des sets perdus par l'équipe (tous matchs joués).
        """
        qs = self._played_qs(obj)
        agg = qs.aggregate(
            home_conceded=Coalesce(Sum(
                Case(When(home_team=obj, then=F('score_away')), default=Value(0), output_field=IntegerField())
            ), 0),
            away_conceded=Coalesce(Sum(
                Case(When(away_team=obj, then=F('score_home')), default=Value(0), output_field=IntegerField())
            ), 0),
        )
        return int(agg['home_conceded'] + agg['away_conceded'])
