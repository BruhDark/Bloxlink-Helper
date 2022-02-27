import discord
from discord.ext import commands
from discord.commands import slash_command
from config import EMOTES, COLORS, RELEASESCOLORS, DESCRIPTION
import time
import json
import urllib
import math
import datetime

class OnConnect(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @slash_command()
    async def stats(self, ctx):
        """View Bloxlink Helper stats"""

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

        request = urllib.request.urlopen("https://railway.instatus.com/summary.json")
        response = json.load(request)

        s = response["page"]
        srailway = s["status"]

        if srailway == "UP":
            srailway =  EMOTES["operational"]
        elif srailway == "HASISSUES":
            srailway = EMOTES["partialoutage"]
        elif srailway == "UNDERMAINTENANCE":
            srailway = EMOTES["maintenance"]
        else:
            srailway = EMOTES["question"]

        pycordV = discord.__version__

        global username
        global icon
        global color
        username = f"{self.bot.user.name}#{self.bot.user.discriminator}"
        icon = self.bot.user.avatar.url
        color = RELEASESCOLORS[f"{self.bot.user.id}"]

        embed = discord.Embed(description=DESCRIPTION, timestamp=datetime.datetime.utcnow(), color=RELEASESCOLORS[f"{self.bot.user.id}"])

        embed.set_author(name=f"{self.bot.user.name}#{self.bot.user.discriminator}", icon_url=self.bot.user.avatar.url)

        global oknos
        oknos = EMOTES[f"{self.bot.user.id}"]

        embed.add_field(name=f"Bot Version", value="?", inline=True)
        embed.add_field(name=":clock1: Uptime", value=uptime, inline=True)
        latency = str(round(self.bot.latency * 1000))
        embed.add_field(name=":ping_pong: Bot Latency", value=f"`{latency}ms`")
        
        embed.add_field(name=":snake: PyCord Version", value=f"{pycordV}", inline=True)
        embed.add_field(name="🚄 Railway Status", value=srailway, inline=True)

        await ctx.respond(embed=embed)

    
    @commands.Cog.listener()
    async def on_connect(self):

         print("Connected.")

         await self.bot.register_commands()

         await self.bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="The support channels"))

         loaded = False

         if not loaded:
             global started
             started = time.time()
             loaded = True

def setup(bot):
    bot.add_cog(OnConnect(bot))