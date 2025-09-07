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


    created_at = models.DateTimeField(auto_now_add=True)

    validation_status_home = models.BooleanField(default=False)
    validation_status_away = models.BooleanField(default=False)
    validation_status_superadmin = models.BooleanField(default=False)

    def __str__(self):
        return f"Match {self.id}: {self.home_team} vs {self.away_team}"


class MatchSet(models.Model):
    SET_TYPES = (
        ('single', 'single'),
        ('double', 'double'),
    )

    match = models.ForeignKey(
        Match,
        on_delete=models.CASCADE,
        related_name='match_sets'
    )

    set_type = models.CharField(max_length=20, choices=SET_TYPES)
    match_identifier = models.CharField(max_length=10, blank=True, null=True)

    # ⬇️ Nouveau : listes de joueurs (au lieu de home_player / away_player)
    home_players = models.ManyToManyField(
        'teams.Player',
        related_name='match_sets_as_home',
        blank=True,
    )
    away_players = models.ManyToManyField(
        'teams.Player',
        related_name='match_sets_as_away',
        blank=True,
    )

    home_points = models.PositiveSmallIntegerField(default=0)
    away_points = models.PositiveSmallIntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        # Optionnel mais conseillé pour éviter les doublons de ligne
        constraints = [
            models.UniqueConstraint(
                fields=['match', 'set_type', 'match_identifier'],
                name='unique_matchset_per_identifier'
            )
        ]

    def __str__(self):
        return f"Set {self.set_type} - {self.match_id} - {self.match_identifier or ''}"
