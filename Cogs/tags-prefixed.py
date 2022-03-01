import discord
from discord.ext import commands
import asyncio
from config import EMOTES, LINKS, COLORS

class TagsPrefixed(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.database = self.bot.database

    async def is_staff(self, ctx: discord.ApplicationContext):

        role = discord.utils.get(ctx.guild.roles, name="Staff")
        permission = ctx.author.guild_permissions.manage_messages

        check = True if role in ctx.author.roles else False

        return True if check or permission else False

    @commands.command()
    async def tag(self, ctx: discord.ApplicationContext, name: str, *, text: str = None):

        name = name.lower()

        collection = self.bot.database["tags"]

        check = {"name": name}
        find = collection.find_one(check)
        if not find:
            check = {"aliases": name}
            find = collection.find_one(check)

        text = text if text is not None else None

        if find:
            if text is not None:
                await ctx.message.delete()
                
                tag = find["content"]

                msg = await ctx.send(f"{tag}")
                await asyncio.sleep(0.1)
                await msg.edit(f"{text} {tag}")


            else:
                await ctx.message.delete()
                
                tag = find["content"]

                await ctx.send(f"{tag}")


        else:
            x = EMOTES["error"]
            embed = discord.Embed(description=f"{x} No tag matching your search.", color=COLORS["error"])
            message = await ctx.send(embed=embed)

            await asyncio.sleep(3.0)
            await message.delete()
            await ctx.message.delete()

    @commands.command()
    async def say(self, ctx: discord.ApplicationContext, *, text: str):
        if await TagsPrefixed.is_staff(self, ctx):
            
            try:
             await ctx.message.delete()
             await ctx.send(text)

            except Exception as e:
                x = EMOTES["error"]
                Embed = discord.Embed(description=f"{x} Something went wrong\n\n```py\n{e}```", color=COLORS["error"])
                await ctx.send(embed=Embed)


        else:
            x = EMOTES["error"]
            embed = discord.Embed(description=f"{x} You do not have permission to run this command.", color=COLORS["error"])
            await ctx.send(embed=embed)

    @commands.command(aliases=["msgedit"])
    async def editmsg(self, ctx: discord.ApplicationContext, id: int, *, text: str):

        if await TagsPrefixed.is_staff(self, ctx):

            message = discord.utils.get(self.bot.cached_messages, id=id)

            try:
              await ctx.message.delete()
              await message.edit(text)

            except Exception as e:
                x = EMOTES["error"]
                Embed = discord.Embed(description=f"{x} Something went wrong\n\n```py\n{e}```", color=COLORS["error"])
                await ctx.send(embed=Embed)

        else:
            x = EMOTES["error"]
            embed = discord.Embed(description=f"{x} You do not have permission to run this command.", color=COLORS["error"])
            await ctx.send(embed=embed, delete_after=3.0)

def setup(bot):
   bot.add_cog(TagsPrefixed(bot))
