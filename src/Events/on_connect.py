import datetime
import json
import math
import time
import urllib

import discord
from config import COLORS, DESCRIPTION, EMOTES, RELEASESCOLORS
from discord.commands import slash_command
from discord.ext import commands


class OnConnect(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_connect(self):

        self.bot.time = time.time()

        print("Connected.")

        await self.bot.register_commands()

        await self.bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="the support channels"))


def setup(bot):
    bot.add_cog(OnConnect(bot))
