from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APITestCase

from teams.models import Team, Player
from .models import Match, MatchSet


class StatsViewDoubleTests(APITestCase):
    def setUp(self):
        team1 = Team.objects.create(club_name="Team A")
        team2 = Team.objects.create(club_name="Team B")

        self.p1 = Player.objects.create(team=team1, first_name="Bob", last_name="Dylan", civility="M")
        self.p2 = Player.objects.create(team=team1, first_name="Jean", last_name="Bernar", civility="M")
        self.p3 = Player.objects.create(team=team2, first_name="Marc", last_name="Antoine", civility="M")
        self.p4 = Player.objects.create(team=team2, first_name="Paul", last_name="Durand", civility="M")

        match = Match.objects.create(
            home_team=team1,
            away_team=team2,
            scheduled_datetime=timezone.now(),
        )
        match_set = MatchSet.objects.create(
            match=match,
            set_type="double",
            match_identifier="DMM1",
            home_points=4,
            away_points=5,
        )
        match_set.home_players.set([self.p1, self.p2])
        match_set.away_players.set([self.p3, self.p4])

    def test_stats_view_returns_pairs(self):
        url = reverse("stats-by-category", args=["doubles-masculins"])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        results = {tuple(r["player_ids"]): r for r in response.data["results"]}
        self.assertIn((self.p1.id, self.p2.id), results)
        pair = results[(self.p1.id, self.p2.id)]
        self.assertEqual(pair["names"], "Bob Dylan / Jean Bernar")
        self.assertEqual(pair["points_scored"], 4)
        self.assertEqual(pair["points_conceded"], 5)
        self.assertIn((self.p3.id, self.p4.id), results)
