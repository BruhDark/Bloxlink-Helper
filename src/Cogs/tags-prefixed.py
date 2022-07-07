import asyncio

import discord
from config import COLORS, EMOTES, LINKS
from discord.ext import commands
from discord.utils import get
from src.resources.CheckFailure import is_staff, is_blacklisted
from src.resources.mongoFunctions import find_tag


class TagsPrefixed(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.guild_only()
    @is_blacklisted()
    async def tag(self, ctx: discord.ApplicationContext, name: str, *, text: str = None):

        find = await find_tag(name)

        text = text if text is not None else None

        message = ctx.message.reference.message_id if ctx.message.reference is not None else None
        message = get(self.bot.cached_messages,
                      id=message) if message is not None else None

        if find:
            if text is not None:
                await ctx.message.delete()

                tag = find["content"]

                if message is not None:
                    msg = await message.reply(content=tag, mention_author=True)
                    await asyncio.sleep(0.1)
                    await msg.edit(f"{text} {tag}")

                else:
                    msg = await ctx.send(f"{tag}")
                    await asyncio.sleep(0.1)
                    await msg.edit(f"{text} {tag}")

            else:
                if message is not None:

                    await ctx.message.delete()

                    tag = find["content"]

                    await message.reply(f"{tag}")

                else:
                    await ctx.message.delete()

                    tag = find["content"]

                    await ctx.send(f"{tag}")

        else:
            x = EMOTES["error"]
            embed = discord.Embed(
                description=f"{x} No tag matching your search.", color=COLORS["error"])
            message = await ctx.send(embed=embed)

            await asyncio.sleep(3.0)
            await message.delete()
            await ctx.message.delete()

    @commands.command()
    @commands.guild_only()
    @is_staff()
    @is_blacklisted()
    async def say(self, ctx: discord.ApplicationContext, *, text: str):
        try:
            await ctx.message.delete()
            await ctx.send(text)

        except Exception as e:
            x = EMOTES["error"]
            Embed = discord.Embed(
                description=f"{x} Something went wrong\n\n```py\n{e}```", color=COLORS["error"])
            await ctx.send(embed=Embed)

    @commands.command(aliases=["msgedit"])
    @commands.guild_only()
    @is_staff()
    @is_blacklisted()
    async def editmsg(self, ctx: discord.ApplicationContext, id: int, *, text: str):
        message = discord.utils.get(self.bot.cached_messages, id=id)

        try:
            await ctx.message.delete()
            await message.edit(text)

        except Exception as e:
            x = EMOTES["error"]
            Embed = discord.Embed(
                description=f"{x} Something went wrong\n\n```py\n{e}```", color=COLORS["error"])
            await ctx.send(embed=Embed)


def setup(bot):
    bot.add_cog(TagsPrefixed(bot))
