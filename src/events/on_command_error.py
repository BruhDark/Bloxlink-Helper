import datetime
import os
import sys
import traceback
from types import NoneType

import aiohttp
import discord
from config import COLORS, EMOTES
from discord.ext import commands


class OnCmdError(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_command_error(self, ctx: commands.Context, error):

        tb = error

        if isinstance(error, commands.CommandOnCooldown):

            x = EMOTES["error"]
            Embed = discord.Embed(
                description=f"{x} This command is on cooldown!", color=COLORS["error"])
            await ctx.send(embed=Embed)

        elif isinstance(error, commands.MissingRequiredArgument):
            pass

        elif isinstance(error, commands.CommandNotFound):
            pass

        elif isinstance(error, commands.NoPrivateMessage):
            x = EMOTES["error"]
            Embed = discord.Embed(
                description=f"{x} This command is only available in a guild!", color=COLORS["error"])
            await ctx.send(embed=Embed)

        elif isinstance(error, commands.CheckFailure):
            x = EMOTES["error"]
            Embed = discord.Embed(
                description=f"{x} {error}", color=COLORS["error"])
            await ctx.send(embed=Embed)

        else:
            x = EMOTES["error"]

            Embed = discord.Embed(
                description=f"{x} Something went wrong\n\n```py\n{tb}```", color=COLORS["error"])
            Embed.set_footer(text="Check #error-logs for more info.")
            await ctx.send(embed=Embed)

            async with aiohttp.ClientSession() as session:
                url = os.getenv("WEBHOOK_URL")
                webhook = discord.Webhook.from_url(url, session=session)
                tb = ''.join(traceback.format_tb(error))
                tb = tb + "\n" + str(error)

                embed = discord.Embed(
                    title=f"{EMOTES['error']} Something Went Wrong", color=COLORS["error"], timestamp=datetime.datetime.utcnow())
                embed.description = f"```py\n{tb}```"
                embed.add_field(
                    name="Command", value=f"{ctx.command.qualified_name}")
                embed.add_field(
                    name="Guild", value=f"{ctx.guild.name} ({ctx.guild.id})")

                await webhook.send(embed=embed)


def setup(bot):
    bot.add_cog(OnCmdError(bot))
