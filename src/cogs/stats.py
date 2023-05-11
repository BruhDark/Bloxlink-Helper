from discord.ext import commands
from discord.commands import slash_command
import discord

import math
import time
import datetime

from config import emotes, colors, releasescolors, DESCRIPTION
from resources.CheckFailure import is_blacklisted


class Stats(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot

    @slash_command()
    @is_blacklisted()
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

        embed = discord.Embed(description="Bloxlink Staff's right hand. Managing tags with useful information and many other automations.", timestamp=datetime.datetime.utcnow(
        ), color=releasescolors.main)

        embed.set_author(
            name=f"{self.bot.user.name}#{self.bot.user.discriminator}", icon_url=self.bot.user.avatar.url)

        embed.add_field(name=f"<:Bot:928765691778203719> Bot Version",
                        value="<:CatPride:1014631162334945410>", inline=True)
        embed.add_field(name=":clock1: Uptime", value=uptime, inline=True)
        latency = str(round(self.bot.latency * 1000))
        embed.add_field(name=":ping_pong: Bot Latency", value=f"{latency}ms")

        embed.add_field(name=":snake: PyCord Version",
                        value=f"{pycordV}", inline=True)

        embed.set_footer(text="Made with ❤️ by the Bloxlink Team")

        await ctx.respond(embed=embed)

    @slash_command()
    async def ping(self, ctx: discord.ApplicationContext):
        """Measure the websocket and API latency"""

        wlatency = str(round(self.bot.latency * 1000))
        embed = discord.Embed(description="⚪ Pinging...", color=colors.info)
                      
        time1 = datetime.datetime.utcnow()
        await ctx.respond(embed=embed)
        time2 = datetime.datetime.utcnow()

        time3 = (time2 - time1)
        alatency = str(round(time3.seconds * 1000))
        embed = discord.Embed(
            description=f"📡 Websocket latency: `{wlatency}ms`\n📦 API Latency: `{alatency}`", color=colors.info)
        embed.set_author(name="🏓 Pong!")
        await ctx.interaction.edit_original_message(embed=embed)
        
    @commands.command(name="ping")
    async def p_ping(self, ctx: commands.Context):
        """Measure the websocket and API latency"""

        wlatency = str(round(self.bot.latency * 1000))
        embed = discord.Embed(description="⚪ Pinging...", color=colors.info)
                      
        time1 = datetime.datetime.utcnow()
        message = await ctx.send(embed=embed)
        time2 = datetime.datetime.utcnow()

        time3 = (time2 - time1)
        alatency = str(round(time3.microseconds / 1000))
        embed = discord.Embed(
            description=f"📡 Websocket latency: `{wlatency}ms`\n📦 API Latency: `{alatency}ms`", color=colors.info)
        embed.set_author(name="🏓 Pong!")
        await message.edit(embed=embed)



def setup(bot):
    bot.add_cog(Stats(bot))
