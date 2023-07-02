import asyncio
import discord
from discord.ext import commands

from resources.context import CommandsContext
from resources.mongoFunctions import find_tag
from resources import webhook_manager


class OnCmdError(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def parse_possible_tag(self, ctx: commands.Context, message: str):

        text = message.split()
        p_tag = text[0].replace(".", "")
        if p_tag == "":
            return

        tag = await find_tag(p_tag)
        text = " ".join(text[1:])
        text = text if text != "" else None

        message = ctx.message.reference.message_id if ctx.message.reference is not None else None
        message = discord.utils.get(
            self.bot.cached_messages, id=message) if message is not None else None

        if tag:
            tag_content = tag["content"]
            if text is not None:
                await ctx.message.delete()

                if message is not None:
                    msg = await message.reply(content=tag_content, mention_author=True)
                    await asyncio.sleep(0.1)
                    await msg.edit(f"{text} {tag_content}")

                else:
                    msg = await ctx.send(f"{tag_content}")
                    await asyncio.sleep(0.1)
                    await msg.edit(f"{text} {tag_content}")

            elif message is not None:

                await ctx.message.delete()
                await message.reply(f"{tag_content}")

            else:
                await ctx.message.delete()
                await ctx.send(f"{tag_content}")

    @commands.Cog.listener()
    async def on_command_error(self, ctx: CommandsContext, error: Exception):

        tb = error

        if isinstance(error, commands.CommandOnCooldown):
            await ctx.error(f"This command is on cooldown! Try again in {round(error.retry_after)} seconds.")

        elif isinstance(error, commands.MemberNotFound):

            await ctx.error("Couldn't find this member.")

        elif isinstance(error, commands.MissingRequiredArgument):
            error: commands.MissingRequiredArgument = error
            await ctx.error(f"You are missing a required argument: `{error.param.name}`")

        elif isinstance(error, commands.CommandNotFound):
            await self.parse_possible_tag(ctx, ctx.message.content)

        elif isinstance(error, commands.NoPrivateMessage):
            await ctx.error("This command is only available in a guild!")

        elif isinstance(error, commands.CheckFailure):
            await ctx.error(error)

        elif isinstance(error, commands.DisabledCommand):
            await ctx.error("This command is disabled!")

        else:
            await webhook_manager.send_command_error(ctx, error)
            await ctx.error(f"Something went wrong\n\n```py\n{tb}```")


def setup(bot):
    bot.add_cog(OnCmdError(bot))
