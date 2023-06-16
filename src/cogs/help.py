import datetime
import discord
from discord import Embed
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
            embed: Embed = discord.Embed(title=emotes.info + " " + name)
            parsed_commands = []
            cmds = list(cog.walk_commands())

            if cmds:
                for command in cmds:
                    print("works2")

                    if isinstance(command, commands.Command):
                        parsed_commands.append(
                            f"\n{command.qualified_name}\n{emotes.reply} {command.description or 'No description provided.'}\n" + "Aliases:" if command.aliases else "" + ",".join(command.aliases) if command.aliases else "")
                        print("works3")

                    elif isinstance(command, discord.ApplicationCommand) and not isinstance(command, discord.UserCommand):
                        parsed_commands.append(
                            f"{command.mention}\n{emotes.reply} {command.description or 'No description provided.'}")
                        print("works4")

                embed.description = "\n".join(parsed_commands)
                embed.color = colors.main
                embed.timestamp = datetime.datetime.utcnow()

                embeds.append(embed)

        for embed in embeds:
            if embed.description is None or embed.description == "":
                embeds.remove(embed)

        paginator = CustomPaginator(
            pages=embeds, disable_on_timeout=True, timeout=60, show_disabled=False)
        await paginator.respond(ctx.interaction)


def setup(bot):
    pass
