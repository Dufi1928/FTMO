from django.db import models


class Player(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self) -> str:
        return self.name


class PlayerStat(models.Model):
    class MatchType(models.TextChoices):
        EQUIPES = 'EQUIPES', 'EQUIPES'
        FEMININES = 'FEMININES', 'FEMININES'
        MASCULINS = 'MASCULINS', 'MASCULINS'
        DOUBLES_MASCULINS = 'DOUBLES_MASCULINS', 'DOUBLES MASCULINS'
        DOUBLES_MASCULIN_FEMININ = 'DOUBLES_MASCULIN_FEMININ', 'DOUBLES MASCULIN-FEMININ'
        JEUNES = 'JEUNES', 'JEUNES'
        DOUBLES_MASCULIN_JEUNE = 'DOUBLES_MASCULIN_JEUNE', 'DOUBLES MASCULIN-JEUNE'
        DOUBLES_FEMININ_JEUNE = 'DOUBLES_FEMININ_JEUNE', 'DOUBLES FEMININ-JEUNE'

    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    category = models.CharField(max_length=32, choices=MatchType.choices)
    sets_won = models.PositiveIntegerField(default=0)
    sets_lost = models.PositiveIntegerField(default=0)

    class Meta:
        unique_together = ('player', 'category')

    def __str__(self) -> str:
        return f"{self.player} - {self.category}"
