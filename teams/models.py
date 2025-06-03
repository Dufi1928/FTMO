from django.db import models


class Team(models.Model):
    club_name = models.CharField(max_length=100)

    image = models.ImageField(          # ← image représentative
        upload_to='teams/images/',      # sous-dossier de MEDIA_ROOT
        blank=True,
        null=True
    )

    team_admin = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='teams_managed'
    )
    email       = models.EmailField(blank=True, null=True)
    updated_at  = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.club_name

class Player(models.Model):

    team = models.ForeignKey(
        'teams.Team',
        on_delete=models.CASCADE,
        related_name='players'
    )
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    civility = models.CharField(max_length=20)  # Par exemple 'Mr', 'Mme', etc.
    email = models.EmailField(blank=True, null=True)
    birth_date = models.DateField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"