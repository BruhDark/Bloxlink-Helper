from discord.ext import commands

class OnReady(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):

     print(f"Ready. Logged in as {self.bot.user} - ID: {self.bot.user.id}")
     print("---------")

def setup(bot):
    bot.add_cog(OnReady(bot))