from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from tinymce.models import HTMLField


class Team(models.Model):
    club_name = models.CharField(max_length=100)
    club_short_description = models.TextField(max_length=100, default="Description courte temporaire")
    club_description_paragraph_1 = HTMLField(default="Description courte temporaire")
    club_description_paragraph_2 = HTMLField(default="Description courte temporaire")

    # Coordonnées géographiques
    latitude = models.DecimalField(
        max_digits=9, decimal_places=6,
        null=True, blank=True,
        validators=[MinValueValidator(-90), MaxValueValidator(90)],
        help_text="Latitude en degrés décimaux (ex: 48.856613)"
    )
    longitude = models.DecimalField(
        max_digits=9, decimal_places=6,
        null=True, blank=True,
        validators=[MinValueValidator(-180), MaxValueValidator(180)],
        help_text="Longitude en degrés décimaux (ex: 2.352222)"
    )
    altitude_m = models.DecimalField(
        max_digits=7, decimal_places=1,
        null=True, blank=True,
        help_text="Altitude en mètres (ex: 35.0)"
    )

    image = models.ImageField(upload_to='teams/images/', blank=True, null=True)
    image_large = models.ImageField(upload_to='teams/images/large/', blank=True, null=True)

    team_admin = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='teams_managed'
    )
    email = models.EmailField(blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.club_name


class AudienceCategory(models.Model):
    class Codes(models.TextChoices):
        JUNIOR = 'junior', 'Jeunes / Juniors'
        SENIOR = 'senior', 'Adultes / Séniors'
        VETERAN = 'veteran', 'Vétérans'

    code = models.CharField(max_length=20, choices=Codes.choices, unique=True)
    label = models.CharField(max_length=50)  # libellé affiché (FR)

    def __str__(self):
        return self.label


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

    team = models.ForeignKey('teams.Team', on_delete=models.CASCADE, related_name='schedules')
    weekday = models.CharField(max_length=3, choices=WEEKDAYS)
    start_time = models.TimeField()
    end_time = models.TimeField()

    # ⬇️ remplace l'ancien champ libre par une M2M multi-sélection
    categories = models.ManyToManyField('teams.AudienceCategory', related_name='schedules', blank=True)

    def __str__(self):
        cats = ", ".join(self.categories.values_list('label', flat=True)) or "Sans catégorie"
        return f"{self.get_weekday_display()} ({self.start_time} - {self.end_time}) • {cats}"


class Player(models.Model):
    team = models.ForeignKey('teams.Team', on_delete=models.CASCADE, related_name='players')
    profile_image = models.ImageField(upload_to='players/images/', blank=True, null=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    civility = models.CharField(max_length=20)  # Par ex. 'Mr', 'Mme'
    email = models.EmailField(blank=True, null=True)
    birth_date = models.DateField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"
