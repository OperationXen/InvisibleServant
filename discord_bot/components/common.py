from discord import Member as DiscordMember
from core.models import Game

from discord_bot.utils.channel import async_remove_discord_member_from_game_channel
from discord_bot.utils.players import async_do_waitlist_updates
from discord_bot.utils.games import async_remove_discord_member_from_game
from core.utils.channels import async_get_game_channel_for_game
from core.utils.players import async_get_player_credit_text

from discord_bot.logs import logger as log


async def handle_player_dropout_event(game: Game, discord_member: DiscordMember) -> bool:
    """handle a player clicking the dropout button"""
    log.debug(f"[>] User {discord_member.display_name} attempted to drop from game {game.name}")

    try:
        removed = await async_remove_discord_member_from_game(discord_member, game)
        await async_do_waitlist_updates(game)
        if removed:
            log.info(f"[>] {discord_member.display_name} dropped from {game.name}")
            games_remaining_text = await async_get_player_credit_text(discord_member)
            await discord_member.send(f"Removed you from {game.name} `({games_remaining_text})`")

            game_channel = await async_get_game_channel_for_game(game)
            if game_channel:
                await async_remove_discord_member_from_game_channel(discord_member, game_channel)
        else:
            log.debug(f"[!] Unable to remove {discord_member.display_name} from {game.name}")
        return removed
    except Exception as e:
        log.error(f"[!] Exception occured handling dropout event: {e}")
