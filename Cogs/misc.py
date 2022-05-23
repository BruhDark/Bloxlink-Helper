import datetime

import discord
from discord.ext import commands
from config import COLORS, EMOTES, LINKS
from Resources.mongoFunctions import find_one, insert_one, delete_one, return_all

s = EMOTES["success2"]
x = EMOTES["error"]


class Misc(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command()
    @commands.is_owner()
    async def blacklist(self, ctx: commands.Context, choice: str, user: discord.Member, *, reason: str = None):
        """Blacklist a user from using the bot."""

        user = self.bot.get_or_fetch_user(user) if type(user) == int else user

        find = await find_one("blacklist", {"user": user.id})
        if find:

            embed = discord.Embed(description=f"{x} {user.mention} is already blacklisted.", color=COLORS["error"])
            await ctx.send(embed=embed)
            return
        
        else:
            insert = await insert_one("blacklist", {"user": user.id, "reason": reason})
            embed = discord.Embed(description=f"{s} {user.mention} has been blacklisted.", color=COLORS["success"])
            embed.add_field(name=":clipboard: Reason", value=reason)
            embed.add_field(name="Item ID", value=insert.inserted_id)
            await ctx.send(embed=embed)
            return


    @commands.command()
    @commands.is_owner()
    async def unblacklist(self, ctx: commands.Context, user: discord.Member):
        """Unblacklist a user from using the bot."""

        user = self.bot.get_or_fetch_user(user) if type(user) == int else user

        find = await find_one("blacklist", {"user": user.id})
        if find:
            await delete_one("blacklist", {"user": user.id})
            s = EMOTES["success2"]
            embed = discord.Embed(description=f"{s} {user.mention} ({user.id}) has been removed from the blacklist.", color=COLORS["success"])
            await ctx.send(embed=embed)

        else:
            s = EMOTES["fail"]
            embed = discord.Embed(description=f"{x} {user.mention} ({user.id}) is not on the blacklist.", color=COLORS["error"])
            await ctx.send(embed=embed)

    @commands.command()
    @commands.is_owner()
    async def blacklistlist(self, ctx: commands.Context):
        """List all blacklisted users."""

        find = await return_all("blacklist")
        for doc in find:
            embed = discord.Embed(title="Blacklisted users", color=COLORS["info"])

            user = await self.bot.get_or_fetch_user(doc["user"])
            reason = doc["reason"] if doc["reason"] else "None"
            embed.add_field(name=f"User: {user.name}#{user.discriminator} ({user.id})", value=f"Reason: {reason}")

        await ctx.send(embed=embed)
        return

def setup(bot):
    bot.add_cog(Misc(bot))
