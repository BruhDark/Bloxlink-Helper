from discord.ext import commands
from discord.commands import slash_command
import discord

import math
import time
import datetime

from config import EMOTES, COLORS, RELEASESCOLORS, DESCRIPTION


class Stats(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @slash_command()
    async def stats(self, ctx: discord.ApplicationContext):
        """View Bloxlink Helper stats"""

        started = self.bot.time

        seconds = math.floor(time.time() - started)

        m, s = divmod(seconds, 60)
        h, m = divmod(m, 60)
        d, h = divmod(h, 24)

        days, hours, minutes, seconds = None, None, None, None

        if d:
            days = f"{d} Days"
        if h:
            hours = f"{h} Hours"
        if m:
            minutes = f"{m} Minutes"
        if s:
            seconds = f"{s} Seconds"

        uptime = f"{days or ''} {hours or ''} {minutes or ''} {seconds or ''}".strip()

        pycordV = discord.__version__

        embed = discord.Embed(description=DESCRIPTION, timestamp=datetime.datetime.utcnow(
        ), color=RELEASESCOLORS[f"{self.bot.user.id}"])

        embed.set_author(
            name=f"{self.bot.user.name}#{self.bot.user.discriminator}", icon_url=self.bot.user.avatar.url)

        embed.add_field(name=f"Bot Version", value="?", inline=True)
        embed.add_field(name=":clock1: Uptime", value=uptime, inline=True)
        latency = str(round(self.bot.latency * 1000))
        embed.add_field(name=":ping_pong: Bot Latency", value=f"`{latency}ms`")

        embed.add_field(name=":snake: PyCord Version",
                        value=f"{pycordV}", inline=True)

        await ctx.respond(embed=embed)

    @slash_command()
    async def ping(self, ctx: discord.ApplicationContext):
        """View Bloxlink Helper latency"""

        latency = str(round(self.bot.latency * 1000))
        embed = discord.Embed(
            description=f"🏓 Latency: `{latency}ms`", color=COLORS['info'])

        await ctx.respond(embed=embed)


def setup(bot):
    bot.add_cog(Stats(bot))
