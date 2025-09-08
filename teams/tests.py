from django.test import TestCase
from django.utils import timezone

from teams.models import Team, Player
from matches.models import Match, MatchSet
from teams.serializers import TeamSerializer


class TeamPlayerStatsTests(TestCase):
    def setUp(self):
        self.team_home = Team.objects.create(club_name="Home Club")
        self.team_away = Team.objects.create(club_name="Away Club")

        self.player1 = Player.objects.create(
            team=self.team_home,
            first_name="Alice",
            last_name="A",
            civility="Mme",
        )
        self.player2 = Player.objects.create(
            team=self.team_home,
            first_name="Bob",
            last_name="B",
            civility="Mr",
        )
        self.player3 = Player.objects.create(
            team=self.team_away,
            first_name="Charlie",
            last_name="C",
            civility="Mr",
        )

        match = Match.objects.create(
            home_team=self.team_home,
            away_team=self.team_away,
            scheduled_datetime=timezone.now(),
            status="played",
        )

        set1 = MatchSet.objects.create(
            match=match,
            set_type="single",
            home_points=11,
            away_points=5,
        )
        set1.home_players.set([self.player1])
        set1.away_players.set([self.player3])

        set2 = MatchSet.objects.create(
            match=match,
            set_type="single",
            home_points=8,
            away_points=11,
        )
        set2.home_players.set([self.player2])
        set2.away_players.set([self.player3])

    def test_player_stats_included_in_team_serializer(self):
        serializer = TeamSerializer(instance=self.team_home)
        data = serializer.data

        players = {p['id']: p for p in data['players']}
        self.assertEqual(players[self.player1.id]['points_won'], 11)
        self.assertEqual(players[self.player1.id]['points_lost'], 5)
        self.assertEqual(players[self.player2.id]['points_won'], 8)
        self.assertEqual(players[self.player2.id]['points_lost'], 11)

        self.assertEqual(data['total_points_scored'], 19)
        self.assertEqual(data['total_points_conceded'], 16)
