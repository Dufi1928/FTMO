from rest_framework import serializers
from .models import Team, Player


class TeamSerializer(serializers.ModelSerializer):
    image = serializers.ImageField(required=False, allow_null=True)

    class Meta:
        model  = Team
        fields = ['id', 'club_name', 'image',
                  'email', 'team_admin', 'updated_at']

class PlayerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Player
        fields = ['id', 'team', 'first_name', 'last_name', 'civility', 'email', 'birth_date']
