# teams/admin.py
from django.contrib import admin
from .models import Team, Schedule, Player, AudienceCategory

@admin.register(AudienceCategory)
class AudienceCategoryAdmin(admin.ModelAdmin):
    list_display = ('code', 'label')
    ordering = ('code',)

@admin.register(Schedule)
class ScheduleAdmin(admin.ModelAdmin):
    list_display = ('team', 'weekday', 'start_time', 'end_time')
    list_filter = ('weekday', 'categories')
    filter_horizontal = ('categories',)

admin.site.register(Team)
admin.site.register(Player)