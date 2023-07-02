from discord.ext import commands

from resources.context import ApplicationCommandsContext
from resources import webhook_manager


class OnApplicationCmdError(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_application_command_error(self, ctx: ApplicationCommandsContext, error: Exception):

        if isinstance(error, commands.CommandOnCooldown):
            await ctx.error(f"This command is on cooldown! Try again in {round(error.retry_after)} seconds.", ephemeral=True)

        elif isinstance(error, commands.NoPrivateMessage):
            await ctx.error(f"This command is only available in a guild!", ephemeral=True)

        elif isinstance(error, commands.CheckFailure):
            await ctx.error(error, ephemeral=True)

        else:

            await webhook_manager.send_command_error(ctx, error)
            await ctx.error(f"Something went wrong\n\n```py\n{error}```")


def setup(bot):
    bot.add_cog(OnApplicationCmdError(bot))
