from discord.ext import commands


class OnReady(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot
        self.ready = False

    @commands.Cog.listener()
    async def on_ready(self):
        if not self.ready:

            print(
                f"✅ Ready! Logged in as {self.bot.user} - ID: {self.bot.user.id}")
            print("-----------------------------------------------------")
            self.ready = True


def setup(bot):
    pass
