import datetime
import traceback
import sys

import discord
from config import COLORS, EMOTES
from discord.ext import commands


class OnCmdError(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_command_error(self, ctx: commands.Context, error):
        if isinstance(error, commands.CommandOnCooldown):

            x = EMOTES["error"]
            Embed = discord.Embed(
                description=f"{x} This command is on cooldown!", color=COLORS["error"])
            await ctx.send(embed=Embed)

        elif isinstance(error, commands.MissingRequiredArgument):
            pass

        elif isinstance(error, commands.CommandNotFound):
            pass

        else:
            x = EMOTES["error"]

            etype, value, tb = sys.exc_info()
            tb = traceback.format_exception(etype, value, tb, None)
            list = ['Traceback (most recent call last):\n']
            list = list + traceback.format_tb(tb, None)

            tb = ''.join(list)

            Embed = discord.Embed(
                description=f"{x} Something went wrong\n\n```py\n{tb}```", color=COLORS["error"])
            await ctx.send(embed=Embed)


def setup(bot):
    bot.add_cog(OnCmdError(bot))
