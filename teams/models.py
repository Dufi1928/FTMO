from django.db import models
from tinymce.models import HTMLField



class Team(models.Model):
    club_name = models.CharField(max_length=100)
    club_short_description = models.TextField(max_length=100, default="Description courte temporaire")
    club_description_paragraph_1 = HTMLField( default="Description courte temporaire")
    club_description_paragraph_2 = HTMLField(default="Description courte temporaire")


    image = models.ImageField(          # ← image représentative
        upload_to='teams/images/',      # sous-dossier de MEDIA_ROOT
        blank=True,
        null=True
    )
    image_large = models.ImageField(          # ← image représentative
        upload_to='teams/images/large/',      # sous-dossier de MEDIA_ROOT
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

class Schedule(models.Model):
    WEEKDAYS = [
        ('mon', 'Lundi'),
        ('tue', 'Mardi'),
        ('wed', 'Mercredi'),
        ('thu', 'Jeudi'),
        ('fri', 'Vendredi'),
        ('sat', 'Samedi'),
        ('sun', 'Dimanche'),
    ]

    team = models.ForeignKey(
        'teams.Team',
        on_delete=models.CASCADE,
        related_name='schedules'
    )
    weekday = models.CharField(max_length=3, choices=WEEKDAYS)
    start_time = models.TimeField()
    end_time = models.TimeField()
    audience_type = models.CharField(max_length=100)  # Valeur libre saisie manuellement

    def __str__(self):
        return f"{self.get_weekday_display()} ({self.start_time} - {self.end_time}) pour {self.audience_type}"


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