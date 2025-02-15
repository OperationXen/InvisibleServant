from django.utils import timezone

from discord.commands import Option
from discord.ext.commands import has_any_role
from discord import Member

from config.settings import DISCORD_GUILDS, DISCORD_ADMIN_ROLES, DISCORD_SIGNUP_ROLES, DISCORD_DM_ROLES
from core.utils.players import async_get_player_credit_text, async_issue_player_bonus_credit
from discord_bot.bot import bot
from discord_bot.utils.time import discord_time
from discord_bot.utils.messaging import async_send_dm
from discord_bot.logs import logger as log


@bot.slash_command(guild_ids=DISCORD_GUILDS, description="Get your current game credit balance")
async def credit(ctx):
    """Show a user their game credit balance"""
    now = timezone.now()
    game_credit_text = await async_get_player_credit_text(ctx.author)
    message = f"As of: {discord_time(now)}\n{game_credit_text}"

    await ctx.respond(message, ephemeral=True, delete_after=30)


@bot.slash_command(guild_ids=DISCORD_GUILDS, description="Award bonus credits to a given user")
@has_any_role(*DISCORD_ADMIN_ROLES, *DISCORD_SIGNUP_ROLES)
async def issue_credit(
    ctx,
    user: Option(Member, "Member to issue bonus games to", required=True),
    reason: Option(str, "Reason for granting the bonus credits", required=False),
    credits: Option(int, "Number of bonus game credits", required=False) = 1,
    expires_after: Option(
        int, "Number of days these credits are valid for (0 or -1 for no expiry)", required=False
    ) = 28,
):
    """issue a game credit to a user"""
    log.info(f"[.] User {ctx.author.name} issued {credits} credit(s) to {user.name} for reason {reason}")
    if expires_after <= 0:
        expires_after = None

    try:
        credit_issued = await async_issue_player_bonus_credit(
            user, credits, ctx.author, reason or "Not given", expires_after
        )
    except Exception as e:
        log.error(f"[!] Exception occured whilst attempting to issue credit: {e}")

    if credit_issued:
        message = f"{ctx.author.name} has awarded you [{credits}] bonus game credits!"
        if expires_after:
            message = f"{message} These will expire in {expires_after} days"
        else:
            message = f"{message} These do not have a fixed expiry time"
        if reason:
            message = message + f"\nReason given: {reason}"
        await async_send_dm(user, message)
        await ctx.respond(f"Game credit awarded to {user.name}", ephemeral=True, delete_after=15)
    else:
        await ctx.respond("Failed to issue credit", ephemeral=True, delete_after=15)


@bot.slash_command(guild_ids=DISCORD_GUILDS, description="Get a users current game credit balance")
@has_any_role(*DISCORD_ADMIN_ROLES, *DISCORD_DM_ROLES)
async def check_credits(ctx, user: Option(Member, "Member to check", required=True)):
    """check current game credit balance"""
    await ctx.defer(ephemeral=True)
    message = await async_get_player_credit_text(user)
    await ctx.respond(message, ephemeral=True)
