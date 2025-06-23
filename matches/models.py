from django.db import models

class Match(models.Model):
    home_team = models.ForeignKey(
        'teams.Team',
        on_delete=models.CASCADE,
        related_name='home_matches'
    )
    away_team = models.ForeignKey(
        'teams.Team',
        on_delete=models.CASCADE,
        related_name='away_matches'
    )

    scheduled_datetime = models.DateTimeField()

    status = models.CharField(max_length=50, default='scheduled')

    global_score_home = models.PositiveSmallIntegerField(default=0)
    global_score_away = models.PositiveSmallIntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)

    validation_status_home = models.BooleanField(default=False)
    validation_status_away = models.BooleanField(default=False)
    validation_status_superadmin = models.BooleanField(default=False)

    def __str__(self):
        return f"Match {self.id}: {self.home_team} vs {self.away_team}"




class MatchSet(models.Model):
    match = models.ForeignKey(
        Match,
        on_delete=models.CASCADE,
        related_name='match_sets'
    )

    set_type = models.CharField(max_length=20)
    match_identifier = models.CharField(max_length=10, blank=True, null=True)

    home_player = models.ForeignKey(
        'teams.Player',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='home_sets'
    )
    away_player = models.ForeignKey(
        'teams.Player',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='away_sets'
    )


    home_points = models.PositiveSmallIntegerField(default=0)
    away_points = models.PositiveSmallIntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Set {self.set_type} - Match {self.match_id}"



