import datetime
from typing import Union

import discord
from discord.ext import commands
from config import COLORS, EMOTES, LINKS
from resources.mongoFunctions import find_one, insert_one, delete_one, return_all

s = EMOTES["success2"]
x = EMOTES["error"]


class Misc(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(aliases=["restrict", "r"])
    @commands.is_owner()
    async def blacklist(self, ctx: commands.Context, user: discord.Member, *, reason: str = None):
        """Blacklist a user from using the bot."""

        user = user if type(user) == int else user.id

        find = await find_one("blacklist", {"user": user})
        if find:

            embed = discord.Embed(
                description=f"{x} <@{user}> is already blacklisted.", color=COLORS["error"])
            await ctx.send(embed=embed)
            return

        else:
            insert = await insert_one("blacklist", {"user": user.id, "reason": reason})
            embed = discord.Embed(description=f"{s} <@{user}> has been blacklisted.",
                                  color=COLORS["success"], timestamp=datetime.datetime.utcnow())
            embed.add_field(name=":clipboard: Reason", value=reason)
            embed.set_footer(text=f"ID: {insert.inserted_id}")
            await ctx.send(embed=embed)
            return

    @commands.command(aliases=["rblacklist"])
    @commands.is_owner()
    async def unblacklist(self, ctx: commands.Context, user: discord.Member):
        """Unblacklist a user from using the bot."""

        user = user if type(user) == int else user.id

        find = await find_one("blacklist", {"user": user.id})
        if find:
            await delete_one("blacklist", {"user": user.id})
            s = EMOTES["success2"]
            embed = discord.Embed(
                description=f"{s} <@{user}> ({user.id}) has been removed from the blacklist.", color=COLORS["success"])
            await ctx.send(embed=embed)

        else:
            s = EMOTES["error"]
            embed = discord.Embed(
                description=f"{x} <@{user}> ({user}) is not on the blacklist.", color=COLORS["error"])
            await ctx.send(embed=embed)

    @commands.command(aliases=["blist"])
    @commands.is_owner()
    async def blacklistlist(self, ctx: commands.Context):
        """List all blacklisted users."""

        info = EMOTES["info"]

        find = await return_all("blacklist")
        for doc in find:
            embed = discord.Embed(
                title=f"{info} Blacklisted users", color=COLORS["info"])

            user = await self.bot.get_or_fetch_user(doc["user"])
            reason = doc["reason"] if doc["reason"] else "None"
            embed.add_field(
                name=f"👤 User: {user.name}#{user.discriminator} ({user.id})", value=f":clipboard: Reason: {reason}")

        await ctx.send(embed=embed)
        return

    @commands.command()
    async def spotify(self, ctx, user: discord.Member = None):
        """Get the spotify status of a user"""

        user: discord.Member = user or ctx.author
        if not isinstance(user.activity, discord.Spotify):
            embed = discord.Embed(
                description=f"{x} {user.mention} is not listening to Spotify or a CustomActivity is blocking me from accessing it.", color=COLORS["error"])
            return await ctx.send(embed=embed)

        else:
            emoji = EMOTES["spotify"]

            Embed = discord.Embed(
                description=f"{user.mention} | {EMOTES['spotify']}", timestamp=datetime.datetime.utcnow(), color=user.color)
            Embed.set_author(
                name=f"{user.name}#{user.discriminator}", icon_url=user.display_avatar.url)

            Embed.set_thumbnail(url=user.activity.album_cover_url)

            artists = user.activity.artists
            duration = user.activity.duration
            durationd = str(duration).split(".")[0]

            Embed.add_field(
                name="Song", value=user.activity.title, inline=False)
            Embed.add_field(name="Duration",
                            value=durationd, inline=True)
            Embed.add_field(name="Artist(s)", value=", ".join(
                artists), inline=False)
            Embed.add_field(
                name="Album", value=user.activity.album, inline=True)

            Embed.set_footer(text=f"ID: {user.id}")

            View = discord.ui.View()
            View.add_item(discord.ui.Button(emoji=emoji, label='Listen on Spotify',
                                            url=user.activity.track_url, style=discord.ButtonStyle.url))
            return await ctx.send(embed=Embed, view=View)

    @commands.command()
    async def error(self, ctx):
        """Error test"""
        raise Exception("Error test")


def setup(bot):
    bot.add_cog(Misc(bot))
