import traceback
import sys

import discord
from config import COLORS, EMOTES
from discord.ext import commands


class OnApplicationCmdError(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_application_command_error(self, ctx, error):

        tb = traceback.format_exception(error)
        tb = "".join(tb)

        if isinstance(error, commands.CommandOnCooldown):

            x = EMOTES["error"]
            Embed = discord.Embed(
                description=f"{x} This command is on cooldown! Try again in {round(error.retry_after)} seconds.", color=COLORS["error"])
            await ctx.respond(embed=Embed, ephemeral=True)

        elif isinstance(error, commands.NoPrivateMessage):

            x = EMOTES["error"]
            Embed = discord.Embed(
                description=f"{x} This command is only available in a guild!", color=COLORS["error"])
            await ctx.respond(embed=Embed, ephemeral=True)

        elif isinstance(error, commands.CheckFailure):

            x = EMOTES["error"]
            Embed = discord.Embed(
                description=f"{x} {error}", color=COLORS["error"])
            await ctx.respond(embed=Embed, ephemeral=True)

        else:
            x = EMOTES["error"]
            
            Embed = discord.Embed(
                description=f"{x} Something went wrong\n\n```py\n{tb}```", color=COLORS["error"])
            await ctx.respond(embed=Embed)


def setup(bot):
    bot.add_cog(OnApplicationCmdError(bot))
