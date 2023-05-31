import datetime
import os
import sys
import traceback
from types import NoneType

import aiohttp
import discord
from config import colors, emotes
from discord.ext import commands

from resources.context import CommandsContext


class OnCmdError(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_command_error(self, ctx: CommandsContext, error: Exception):

        tb = error

        if isinstance(error, commands.CommandOnCooldown):
            await ctx.error(f"This command is on cooldown! Try again in {round(error.retry_after)} seconds.")

        elif isinstance(error, commands.MemberNotFound):

            await ctx.error("Couldn't find this member.")

        elif isinstance(error, commands.MissingRequiredArgument):
            error: commands.MissingRequiredArgument = error
            await ctx.error(f"You are missing a required argument: `{error.param.name}`")

        elif isinstance(error, commands.CommandNotFound):
            pass

        elif isinstance(error, commands.NoPrivateMessage):
            await ctx.error("This command is only available in a guild!")

        elif isinstance(error, commands.CheckFailure):
            await ctx.error(error)

        elif isinstance(error, commands.DisabledCommand):
            await ctx.error("This command is disabled!")

        else:
            await ctx.error(f"Something went wrong\n\n```py\n{tb}```")

            async with aiohttp.ClientSession() as session:
                url = os.getenv("WEBHOOK_URL")
                webhook = discord.Webhook.from_url(url, session=session)
                tb = ''.join(traceback.format_exception(
                    error, error, error.__traceback__))
                tb = tb + "\n"

                embed = discord.Embed(
                    title=f"{emotes.error} Something Went Wrong", color=colors.error, timestamp=datetime.datetime.utcnow())
                embed.description = f"```py\n{tb}```"
                embed.add_field(
                    name="Command", value=f"{ctx.command.qualified_name}")
                embed.add_field(
                    name="Guild", value=f"{ctx.guild.name} ({ctx.guild.id})")

                await webhook.send(embed=embed)


def setup(bot):
    bot.add_cog(OnCmdError(bot))
