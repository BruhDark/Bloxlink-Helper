import datetime
from typing import Union

import discord
from discord.ext import commands
from config import colors, emotes, links
from resources.mongoFunctions import find_one, insert_one, delete_one, return_all

s = emotes.success2
x = emotes.error


class Misc(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command()
    async def spotify(self, ctx, user: discord.Member = None):
        """Get the spotify status of a user"""

        user: discord.Member = user or ctx.author
        if not isinstance(user.activity, discord.Spotify):
            embed = discord.Embed(
                description=f"{x} {user.mention} is not listening to Spotify or a CustomActivity is blocking me from accessing it.", color=colors.error)
            return await ctx.send(embed=embed)

        else:
            emoji = emotes.spotify

            Embed = discord.Embed(
                description=f"{user.mention} | {emotes.spotify}", timestamp=datetime.datetime.utcnow(), color=user.color)
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

    @commands.command()
    async def blacklist(self, ctx: commands.Context, option: str, user: discord.User, reason: str = "Not specified"):

        if option.lower() == "add":
            if find_one("blacklist", {"user": user.id}):
                await ctx.send(f"{emotes.error} This user is already blacklisted", color=colors.error)
                return

            insert_one("blacklist", {"user": user.id, "reason": reason})
            await ctx.send(f"{emotes.success2} Added this user ({user.mention}) to the blacklist with reason: {reason}")

        elif option.lower() == "remove":
            if not find_one("blacklist", {"user": user.id}):
                await ctx.send(f"{emotes.error} This user is not blacklisted", color=colors.error)
                return

            delete_one("blacklist", {"user": user.id})
            await ctx.send(f"{emotes.success2} Removed this user ({user.mention}) from the blacklist.")

        elif option.lower() == "show":

            blacklists: list = return_all("blacklist")
            parse_blacklists = [
                f"User: {blacklist['user']}. Reason: {blacklist['reason']}" for blacklist in blacklists]
            final_parse = "\n".join(parse_blacklists)

            await ctx.send(content=final_parse)


def setup(bot):
    bot.add_cog(Misc(bot))
