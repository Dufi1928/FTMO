from django.contrib import admin

# Register your models here.
from .models import Match, MatchSet

admin.site.register(Match)
admin.site.register(MatchSet)