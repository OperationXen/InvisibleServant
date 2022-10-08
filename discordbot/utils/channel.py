import random
from discord import PermissionOverwrite

from discordbot.bot import bot
from discordbot.logs import logger as log
from config.settings import CHANNEL_SEND_PINGS
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

async def _get_mustering_view_for_game(game):
    """ Given a game object, check its mustering channel and retrieve the view attached to the mustering embed"""
    for view in bot.persistent_views:
        view_name = str(type(view))
        if 'MusteringView' in view_name and view.game == game:
            return view
    return None

async def update_mustering_embed(game):
    """ Refresh a mustering embed for a specific game """
    try:
        view = await _get_mustering_view_for_game(game)
        if view:
            return await view.update_message()
    except Exception as e:
        log.debug(f"Error when updating associated muster embed")
    return False

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
    if CHANNEL_SEND_PINGS:
        user_text = user.mention
    else:
        user_text = user.display_name

    choices = [
        f"{user_text} joins the party", 
        f"Welcome to the party {user_text}", 
        f"A wild {user_text} appears!", 
        f"{user_text} emerges from the mists",
        f"A rogue portal appears and deposits {user_text}", 
        f"Is that 3 kobolds in an overcoat? No! its {user_text}",
        f"The ritual is complete, {user_text} walks amongst us",
        f"{user_text} planeshifts in",
        f"Congratulations {user_text}, you have been selected, please do not resist.",
        f"{user_text} broods in the corner of the tavern",
        f"Neither snow nor rain nor heat nor gloom of night could stop {user_text} from joining this party",
        f"Neither snow nor rain nor heat nor glom of nit could stop {user_text} from joining this party",
        f"It's not a doppelganger, it's {user_text}",
        f"{user_text} teleports in with a shower of confetti",
        f"I would like to cast Player Ally and summon {user_text}",
        f"Everyone knows something is afoot when {user_text} arrives...",
        f"{user_text} has been successfully planar bound to this session!",
        f"BAM! A three point landing like that can only be {user_text}.",
        f"After succeeding on a perception check, you find {user_text} has snuck into the game. "
        ]

    message = random.choice(choices)
    message = await notify_game_channel(game, message)

async def game_channel_tag_promoted_player(game, player):
    """ Tag a user in a channel from a player object"""
    discord_user = await bot.fetch_user(player.discord_id)
    return await game_channel_tag_promoted_user(game, discord_user)

async def game_channel_tag_removed_user(game, user):
    """Send a message to the game channel notifying the DM that a player has dropped"""
    message = f"{user.display_name} dropped out"
    message = await notify_game_channel(game, message)

async def channel_add_user(channel, user):
    """Give a specific user permission to view and post in the channel for an upcoming game"""
    try:
        await channel.set_permissions(user, read_messages=True)
        return True
    except Exception as e:
        log.debug(f"Exception occured adding discord user {user.name} to channel")
    return False

async def channel_add_player(channel, player):
    """ Add a user to channel by reference from a player object"""
    log.info(f"Adding player [{player.discord_name}] to channel [{channel.name}]")
    try:
        discord_user = await bot.fetch_user(player.discord_id)
        return await channel_add_user(channel, discord_user)
    except:
        log.error(f"Unable to add this player to the channel")
    return None
    
async def channel_remove_user(channel, user):
    """Remove a specific player from a game channel"""
    try:
        log.info(f"Removing player [{user.display_name}] from channel [{channel.name}]")
        await channel.set_permissions(user, read_messages=False)
        return True
    except Exception as e:
        log.debug(f"Exception occured removing discord user {user.discord_name} from channel")
    return False

async def create_channel_hidden(guild, parent, name, topic):
    """creates a channel which can only be seen and used by the bot"""
    log.info(f"Creating new game mustering channel: {name} ")
    overwrites = {
        guild.default_role: PermissionOverwrite(read_messages=False),
        guild.me: PermissionOverwrite(read_messages=True),
    }
    channel = await guild.create_text_channel(category=parent, name=name, topic=topic, overwrites=overwrites)
    return channel

async def get_all_game_channels_for_guild(guild):
    """ List all existing game channels """
    all_channels = guild.by_category()
    for channel_group in all_channels:
        if channel_group[0].name == 'Your Upcoming Games':
            return channel_group[1]
    return []

async def get_channel_first_message(channel):
    """ Get the first message in a specified channel """
    message = await channel.history(limit=1, oldest_first=True).flatten()
    return message[0]
