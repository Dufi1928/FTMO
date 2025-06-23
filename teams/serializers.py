from rest_framework import serializers
from .models import Team, Player, Schedule

class PlayerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Player
        fields = ['id', 'team', 'first_name', 'last_name', 'civility', 'email', 'birth_date']

class ScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Schedule
        fields = ['id', 'weekday', 'start_time', 'end_time', 'audience_type']

class TeamSerializer(serializers.ModelSerializer):
    players = PlayerSerializer(many=True, read_only=True)
    schedules = ScheduleSerializer(many=True, read_only=True)

    class Meta:
        model = Team
        fields = [
            'id', 'club_name','club_description_paragraph_1','club_description_paragraph_2', 'image', 'image_large',
            'team_admin', 'email', 'updated_at',
            'players', 'schedules'
        ]




