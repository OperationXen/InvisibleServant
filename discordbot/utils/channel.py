from discord import PermissionOverwrite

from discordbot.bot import bot
from discordbot.logs import logger as log
from core.utils.channels import get_game_channel_for_game


async def get_channel_for_game(game):
    """Get a discord object for a given game"""
    try:
        game_channel = await get_game_channel_for_game(game)
        channel = bot.get_channel(int(game_channel.discord_id))
        return channel
    except Exception as e:
        log.debug(f"Unable to get an active channel for {game.name}")
    return None


async def notify_game_channel(game, message):
    """Send a notification to a game channel"""
    channel = await get_channel_for_game(game)
    if channel:
        log.debug(f"Sending channel message to {channel.name}. Message: {message}")
        status = await channel.send(message)
        return status
    else:
        log.debug(f"Cannot send message to non-existant channel")
    return False


async def game_channel_tag_promoted_user(game, user):
    """Send a message to the game channel notifying the player that they've been promoted"""
    message = f"<@{user.mention}> promoted from waitlist"
    message = await notify_game_channel(game, message)


async def game_channel_tag_removed_user(game, user):
    """Send a message to the game channel notifying the DM that a player has dropped"""
    message = f"{user.display_name} dropped out"
    message = await notify_game_channel(game, message)


async def channel_add_player(channel, player):
    """Give a specific player permission to view and post in the channel for an upcoming game"""
    try:
        log.info(f"Adding player [{player.discord_name}] to channel [{channel.name}]")
        discord_user = await bot.fetch_user(player.discord_id)
        await channel.set_permissions(discord_user, read_messages=True, send_messages=True)
        return True
    except Exception as e:
        log.debug(f"Exception occured adding player to channel")
    return False


async def channel_remove_user(channel, user):
    """Remove a specific player from a game channel"""
    try:
        log.info(f"Removing player [{user.display_name}] from channel [{channel.name}]")
        await channel.set_permissions(user, read_messages=False, send_messages=False)
        return True
    except Exception as e:
        log.debug(f"Exception occured removing player from channel")
    return False


async def create_channel_hidden(guild, parent, name, topic):
    """creates a channel which can only be seen and used by the bot"""
    log.info(f"Creating new game mustering channel: {name} ")
    overwrites = {
        guild.default_role: PermissionOverwrite(read_messages=False, send_messages=False),
        guild.me: PermissionOverwrite(read_messages=True, send_messages=True),
    }
    channel = await guild.create_text_channel(category=parent, name=name, topic=topic, overwrites=overwrites)
    return channel
