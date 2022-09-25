from discord.ext import tasks
from discord.utils import get

from discordbot.logs import logger as log
from discordbot.utils.time import get_hammertime
from core.utils.games import get_dm, get_player_list
from core.utils.channels import get_game_channels_pending_creation, set_game_channel_created
from core.utils.channels import get_game_channels_pending_destruction, destroy_game_channel
from core.utils.channels import get_game_channels_pending_reminder, set_game_channel_reminded
from core.utils.channels import get_game_channels_pending_warning, set_game_channel_warned
from core.utils.channels import get_game_channel_for_game
from discordbot.components.channels import MusteringBanner, MusteringView


class ChannelManager:
    """Manager class for performing channel based functions"""
    initialised = False
    guild = None
    parent_category = None

    def __init__(self, guild):
        """ initialisation function """
        self.guild = guild
        self.channel_event_loop.start()

    async def get_topic_text(self, game):
        """ build the game channel topic header """
        dm = await get_dm(game)
        topic_text = "This thread is for mustering for the following game: "
        topic_text+= f"{game.module} ({game.name}) | DMed by {dm.name} | "
        topic_text+= f"Game is scheduled for {get_hammertime(game.datetime)}"
        return topic_text

    async def get_ping_text(self, game):
        players = await get_player_list(game)
        ping_text = 'Players: '
        ping_text+= ','.join(f"<@{p.discord_id}>" for p in players if not p.standby)
        return ping_text

    async def send_banner_message(self, channel, game):
        """send the welcome banner"""
        control_view = MusteringView(game)
        banner = MusteringBanner(game)
        await banner.build()

        ping_text = await self.get_ping_text(game)
        message = await channel.send(ping_text, embed=banner, view=control_view)
        control_view.message = message

    async def check_and_create_channels(self):
        """ Get outstanding channels needed and create them where missing """
        pending_games = await get_game_channels_pending_creation()
        for upcoming_game in pending_games:
            log.info(f"Creating channel for game: {upcoming_game.name}")
            channel_name = upcoming_game.datetime.strftime("%Y%m%d-") + upcoming_game.module            
            channel_topic = await self.get_topic_text(upcoming_game)
            channel = await self.guild.create_text_channel(category=self.parent_category, name=channel_name, topic=channel_topic)
            if channel:
                game_channel = await set_game_channel_created(upcoming_game, channel.id, channel.jump_url, channel.name)
                await self.send_banner_message(channel, upcoming_game)

    async def check_and_delete_channels(self):
        """ Go through any outstanding channels and delete anything older than 3 days """
        try:
            expired_game_channels = await get_game_channels_pending_destruction()
            for game_channel in expired_game_channels:
                log.info(f"Removing game channel: {game_channel.name}")
                channel = self.guild.get_channel(int(game_channel.discord_id))
                await channel.delete()
                await destroy_game_channel(game_channel)
        except Exception as e:
            log.error(e)

    async def check_and_remind_channels(self):
        """ Remind players 24 hours before their game """
        try:
            upcoming_games = await get_game_channels_pending_reminder()
            for game in upcoming_games:
                game_channel = await get_game_channel_for_game(game)
                log.info(f"Sending game reminder to channel: {game_channel.name}")
                channel = self.guild.get_channel(int(game_channel.discord_id))
                ping_text = await self.get_ping_text(game)
                await channel.send(f"Reminder: this game starts in 24 hours\n{ping_text}")
                await set_game_channel_reminded(game_channel)
        except Exception as e:
            log.error(e)

    async def check_and_warn_channels(self):
        """ Remind players 1 hour before their game """
        try:
            upcoming_games = await get_game_channels_pending_warning()
            for game in upcoming_games:
                game_channel = await get_game_channel_for_game(game)
                log.info(f"Sending 1 hour start warning to channel: {game_channel.name}")
                channel = self.guild.get_channel(int(game_channel.discord_id))
                ping_text = await self.get_ping_text(game)
                await channel.send(f"Game starts in 1 hour, please ensure that you are ready\n{ping_text}")
                await set_game_channel_warned(game_channel)
        except Exception as e:
            log.error(e)

    @tasks.loop(seconds=60)
    async def channel_event_loop(self):
        if not self.initialised:
            log.debug('Starting up the channel watcher')
            self.parent_category = get(self.guild.categories, name="Upcoming Games")
            self.initialised = True

        await self.check_and_create_channels()
        await self.check_and_delete_channels()
        await self.check_and_remind_channels()
        await self.check_and_warn_channels()
