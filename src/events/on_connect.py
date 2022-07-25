import time

from config import COLORS, DESCRIPTION, EMOTES, RELEASESCOLORS
from discord.commands import slash_command
from discord.ext import commands


class OnConnect(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot

    @commands.Cog.listener()
    async def on_connect(self):
        self.bot.time = time.time()


def setup(bot):
    bot.add_cog(OnConnect(bot))
