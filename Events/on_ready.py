from discord.ext import commands
import discord

class OnReady(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):

     loaded = False

     if not loaded:
         await self.bot.change_presence(status=discord.Status.online, activity=discord.Activity(type=discord.ActivityType.watching, name="the support channels"))
         loaded = True

     print(f"Ready. Logged in as {self.bot.user} - ID: {self.bot.user.id}")
     print("---------")

def setup(bot):
    bot.add_cog(OnReady(bot))