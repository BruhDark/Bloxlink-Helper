from datetime import datetime
import os
import sys
import traceback

import aiohttp
import discord
from config import colors, emotes
from discord.ext import commands


class OnApplicationCmdError(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_application_command_error(self, ctx: discord.ApplicationContext, error: Exception):

        if isinstance(error, commands.CommandOnCooldown):

            x = emotes.error
            Embed = discord.Embed(
                description=f"{x} This command is on cooldown! Try again in {round(error.retry_after)} seconds.", color=colors.error)
            await ctx.respond(embed=Embed, ephemeral=True)

        elif isinstance(error, commands.NoPrivateMessage):

            x = emotes.error
            Embed = discord.Embed(
                description=f"{x} This command is only available in a guild!", color=colors.error)
            await ctx.respond(embed=Embed, ephemeral=True)

        elif isinstance(error, commands.CheckFailure):

            x = emotes.error
            Embed = discord.Embed(
                description=f"{x} {error}", color=colors.error)
            await ctx.respond(embed=Embed, ephemeral=True)

        else:
            x = emotes.error

            Embed = discord.Embed(
                description=f"{x} Something went wrong\n\n```py\n{error}```", color=colors.error)

            await ctx.respond(embed=Embed)

            async with aiohttp.ClientSession() as session:
                url = os.getenv("WEBHOOK_URL")
                webhook = discord.Webhook.from_url(url, session=session)
                tb = ''.join(traceback.format_exception(
                    error, error, error.__traceback__))
                tb = tb + "\n"

                embed = discord.Embed(
                    title=f"{emotes.error} Something Went Wrong", color=colors.error, timestamp=datetime.utcnow())
                embed.description = f"```py\n{tb}```"
                embed.add_field(
                    name="Command", value=f"{ctx.command.qualified_name}")
                embed.add_field(
                    name="Guild", value=f"{ctx.guild.name} ({ctx.guild.id})")

                await webhook.send(embed=embed)


def setup(bot):
    bot.add_cog(OnApplicationCmdError(bot))
