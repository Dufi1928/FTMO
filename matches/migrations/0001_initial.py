from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ('teams', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Match',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('scheduled_datetime', models.DateTimeField()),
                ('status', models.CharField(default='scheduled', max_length=50)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('validation_status_home', models.BooleanField(default=False)),
                ('validation_status_away', models.BooleanField(default=False)),
                ('validation_status_superadmin', models.BooleanField(default=False)),
                ('away_team', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='away_matches', to='teams.team')),
                ('home_team', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='home_matches', to='teams.team')),
            ],
        ),
        migrations.CreateModel(
            name='MatchSet',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('set_type', models.CharField(max_length=20)),
                ('match_identifier', models.CharField(blank=True, max_length=10, null=True)),
                ('home_points', models.PositiveSmallIntegerField(default=0)),
                ('away_points', models.PositiveSmallIntegerField(default=0)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('away_players', models.ManyToManyField(blank=True, related_name='match_sets_as_away', to='teams.player')),
                ('home_players', models.ManyToManyField(blank=True, related_name='match_sets_as_home', to='teams.player')),
                ('match', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='match_sets', to='matches.match')),
            ],
            options={
                'constraints': [
                    models.UniqueConstraint(fields=['match', 'set_type', 'match_identifier'], name='unique_matchset_per_identifier'),
                ],
            },
        ),
    ]
