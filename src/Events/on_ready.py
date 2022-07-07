import discord
from discord.ext import commands


class OnReady(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.ready = False

    @commands.Cog.listener()
    async def on_ready(self):
        if not self.ready:
         print(f"✅ Ready! Logged in as {self.bot.user} - ID: {self.bot.user.id}")
         print("-----------------------------------------------------")
         print("🕵️‍♂️ Changing presence...")
         await self.bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="the support channels | blox.link"))
         print("🕵️‍♂️ Changed presence!")
         self.ready = True


def setup(bot):
    bot.add_cog(OnReady(bot))
