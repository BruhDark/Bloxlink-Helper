from discord.ext import commands
import discord
from resources.context import ApplicationCommandsContext, CommandsContext
from resources.mongoFunctions import find_one


class NotStaff(commands.CheckFailure):
    pass


def is_staff():
    async def predicate(ctx: CommandsContext or ApplicationCommandsContext):
        if await ctx.bot.is_owner(ctx.author):
            return True

        helpers = ctx.guild.get_role(412791520316358656)
        mods = ctx.guild.get_role(372174398918098944)
        developer = ctx.guild.get_role(539665515430543360)
        permission = ctx.author.guild_permissions.manage_messages

        if any([role in ctx.author.roles for role in (helpers, mods, developer)]) or permission:
            return True
        raise NotStaff("You are not allowed to use this command")
    return commands.check(predicate)


class Blacklisted(commands.CheckFailure):
    pass


def is_blacklisted():
    async def predicate(ctx):

        check = {"user": ctx.author.id}
        find = await find_one("blacklist", check)

        if find:
            reason = find["reason"]
            raise Blacklisted(
                f"You are blacklisted from using this bot: `{reason}`")
        return True
    return commands.check(predicate)
