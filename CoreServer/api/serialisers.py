from rest_framework.serializers import ModelSerializer, ReadOnlyField, SerializerMethodField

from core.models import Game

class GameSerialiser(ModelSerializer):
    """ Serialiser for game objects """
    id = ReadOnlyField(source='pk')
    dm_name = ReadOnlyField(source='dm.name')

    number_of_players = SerializerMethodField()
    number_of_waitlisted = SerializerMethodField()

    def get_number_of_players(self, game):
        """ Retrieve the current number of players for a given game """
        players = game.players.filter(standby=False)
        return players.count()

    def get_number_of_waitlisted(self, game):
        """ Retrieve the current number of players waitlisted for the specified game """
        players = game.players.filter(standby=True)
        return players.count()

    class Meta:
        model = Game
        fields = ['id', 'dm_name', 'name', 'module', 'realm', 'variant', 'description', 'number_of_players', 'number_of_waitlisted', 'max_players', 'level_min', 'level_max', 'warnings', 'channel', 'streaming', 'datetime_release', 'datetime_open_release', 'datetime', 'length']
