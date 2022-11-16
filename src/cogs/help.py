import datetime
import discord
from discord.ext import commands
from resources.context import ApplicationCommandsContext
from config import colors, emotes
from resources.paginator import CustomPaginator


class Help(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot

    @commands.slash_command()
    async def help(self, ctx: ApplicationCommandsContext):

        await ctx.defer()

        embeds = []

        for name, cog in self.bot.cogs.items():
            embed = discord.Embed(title=emotes.info + " " + name)
            parsedCommands = []
            cmds = list(cog.walk_commands())

            if cmds:
                for command in cmds:
                    print("works2")

                    if isinstance(command, commands.Command):
                        parsedCommands.append(
                            f"\n{command.qualified_name}\n{emotes.reply} {command.description or 'No description provided.'}\n" + "Aliases:" if command.aliases else "" + ",".join(command.aliases) if command.aliases else "")
                        print("works3")

                    elif isinstance(command, discord.ApplicationCommand) and not isinstance(command, discord.UserCommand):
                        parsedCommands.append(
                            f"{command.mention}\n{emotes.reply} {command.description or 'No description provided.'}")
                        print("works4")

                embed.description = "\n".join(parsedCommands)
                embed.color = colors.main
                embed.timestamp = datetime.datetime.utcnow()

                embeds.append(embed)

        for embed in embeds:
            if embed.description == None or embed.description == "":
                embeds.remove(embed)

        paginator = CustomPaginator(
            pages=embeds, disable_on_timeout=True, timeout=60, show_disabled=False)
        await paginator.respond(ctx.interaction)


def setup(bot):
    pass
