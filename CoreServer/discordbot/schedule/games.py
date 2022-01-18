from discord.ext import tasks

from config.settings import DEFAULT_CHANNEL_NAME, PRIORITY_CHANNEL_NAME
from discordbot.utils.messaging import get_channel_by_name, get_bot_game_postings, get_guild_channel
from discordbot.components.banners import GameAnnounceBanner
from discordbot.components.games import GameDetailEmbed, GameControlView
from core.utils.games import get_outstanding_games, set_game_announced

class GamesPoster():
    initialised = False
    messages_priority = []
    messages_general = []

    channel_general = None
    channel_priority = None

    def __init__(self):
        """ initialisation function """
        print("Starting scheduled update daemon...")
        self.check_and_post_games.start()

    async def startup(self):
        await self.get_channels()
        await self.recover_message_state()
        self.initialised = True

    async def announce_games(self, games, priority=False):
        for game in games:
            await self.do_game_announcement(game, priority)
            await set_game_announced(game)

    async def get_channels(self):
        """ Recover channels give identifiers """
        self.channel_general = await get_guild_channel(DEFAULT_CHANNEL_NAME)
        self.channel_priority = await get_guild_channel(PRIORITY_CHANNEL_NAME)

    async def do_game_announcement(self, game, priority):
        """ Build an announcement """
        if priority:
            channel = self.channel_priority
        else:
            channel = self.channel_general

        embeds = [GameAnnounceBanner(priority=priority)]
        details_embed = GameDetailEmbed(game)
        await details_embed.build()
        embeds.append(details_embed)

        control_view = GameControlView(game)
        if channel:
            control_view.message = await channel.send(embeds=embeds, view=control_view)

    async def post_outstanding_games(self):
        """ Create new messages for any games that need to be announced """
        # get games for general release
        outstanding_games = await get_outstanding_games(priority=False)
        await self.announce_games(outstanding_games, priority=False)

        # get games for priority release
        outstanding_games = await get_outstanding_games(priority=True)
        await self.announce_games(outstanding_games, priority=True)

    async def recover_message_state(self):
        """ Read the channels and reconnect messages """
        self.messages_priority = await get_bot_game_postings(self.channel_general)
        self.messages_general = await get_bot_game_postings(self.channel_priority)

    async def remove_stale_games(self, channel):
        """ Go through all existing game messages and check for anything stale """
        pass
        
    @tasks.loop(seconds=10)
    async def check_and_post_games(self):
        if not self.initialised:
            await self.startup()

        if self.channel_priority and self.channel_general:
            await self.remove_stale_games()
            await self.post_outstanding_games()
        
    
scheduled_poster = GamesPoster()
