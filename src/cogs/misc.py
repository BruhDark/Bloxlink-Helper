import datetime
from typing import Union

import discord
from discord.ext import commands
from config import colors, emotes, links
from resources.context import CommandsContext
from resources.mongoFunctions import find_one, insert_one, delete_one, return_all

s = emotes.success2
x = emotes.error


class Misc(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(description="See what's someone listening to")
    async def spotify(self, ctx, user: discord.Member = None):

        user: discord.Member = user or ctx.author
        activity = None
        activity = user.activity if isinstance(
            user.activity, discord.Spotify) else None

        if activity is None:
            for act in user.activities:
                if isinstance(act, discord.Spotify):
                    activity = act
                    break

        if activity is None:
            embed = discord.Embed(
                description=f"{x} {user.mention} is not listening to Spotify.", color=colors.error)
            return await ctx.send(embed=embed)

        else:
            emoji = emotes.spotify

            Embed = discord.Embed(
                description=f"{user.mention} | {emotes.spotify}", timestamp=datetime.datetime.utcnow(), color=user.color)
            Embed.set_author(
                name=f"{user.name}#{user.discriminator}", icon_url=user.display_avatar.url)

            Embed.set_thumbnail(url=activity.album_cover_url)

            artists = activity.artists
            duration = activity.duration
            durationd = str(duration).split(".")[0]

            Embed.add_field(
                name="Song", value=activity.title, inline=False)
            Embed.add_field(name="Duration",
                            value=durationd, inline=True)
            Embed.add_field(name="Artist(s)", value=", ".join(
                artists), inline=False)
            Embed.add_field(
                name="Album", value=activity.album, inline=True)

            Embed.set_footer(text=f"ID: {user.id}")

            View = discord.ui.View()
            View.add_item(discord.ui.Button(emoji=emoji, label='Listen on Spotify',
                                            url=activity.track_url, style=discord.ButtonStyle.url))
            return await ctx.send(embed=Embed, view=View)

    @commands.command(description="Raise an intentional error")
    async def error(self, ctx):
        """Error test"""
        raise Exception("Error test")

    @commands.command(description="Blacklist a user")
    @commands.is_owner()
    async def blacklist(self, ctx: CommandsContext, option: str, user: discord.User, *, reason: str = "Not specified"):

        if option.lower() == "add":
            if await find_one("blacklist", {"user": user.id}):
                await ctx.error(f"This user is already blacklisted")
                return

            await insert_one("blacklist", {"user": user.id, "reason": reason})
            await ctx.success(f"Added this user ({user.mention}) to the blacklist with reason: {reason}")

        elif option.lower() == "remove":
            if not await find_one("blacklist", {"user": user.id}):
                await ctx.error(f"This user is not blacklisted")
                return

            await delete_one("blacklist", {"user": user.id})
            await ctx.success(f"Removed this user ({user.mention}) from the blacklist.")

        elif option.lower() == "show":

            blacklists: list = await return_all("blacklist")
            parse_blacklists = [
                f"User: {blacklist['user']}. Reason: {blacklist['reason']}" for blacklist in blacklists]
            final_parse = "\n".join(parse_blacklists)

            await ctx.send(content=final_parse)

        else:
            await ctx.error(f"That option does not exist!")


def setup(bot):
    bot.add_cog(Misc(bot))
