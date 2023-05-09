import datetime
import io

import aiohttp
import discord
from discord.ext import commands

from config import colors, emotes, links
from resources.context import CommandsContext
from resources.mongoFunctions import (delete_one, find_one, insert_one,
                                      return_all)

s = emotes.success2
x = emotes.error


class Misc(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(aliases=["av"])
    async def avatar(self, ctx: CommandsContext, user: discord.Member = None):
        user = user or ctx.author

        embed = discord.Embed(color=user.color if user.color !=
                              discord.Color.default else colors.main)
        embed.set_image(url=user.display_avatar.url)
        embed.set_author(name=str(user), icon_url=user.display_avatar.url)
        embed.timestamp = datetime.datetime.utcnow()

        await ctx.reply(embed=embed, mention_author=False)

    @commands.command(aliases=["setpfp", "setav"])
    @commands.is_owner()
    async def setavatar(self, ctx: CommandsContext, link: str):
        async with aiohttp.ClientSession() as session:
            async with session.get(link) as resp:
                img = await resp.read()
                with io.BytesIO(img) as file:
                    await self.bot.user.edit(avatar=file.getvalue())
                    await ctx.success("Successfully changed my avatar", True)

    @commands.command(description="See what's someone listening to", aliases=["sp"])
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

            await ctx.reply(content=final_parse, mention_author=False)

        else:
            await ctx.error(f"That option does not exist!")

    @commands.command()
    @commands.is_owner()
    async def maintenance(self, ctx: CommandsContext, reason: str = "Maintenance"):
        if not self.bot.maintenance:
            self.bot.maintenance = True
            self.bot.changing_presence.cancel()
            await self.bot.change_presence(status=discord.Status.do_not_disturb, activity=discord.Game(reason))
            await ctx.success("Maintenance mode is now active.")

        else:
            self.bot.maintenance = False
            await self.bot.change_presence(status=discord.Status.online)
            self.bot.changing_presence.start()

            await ctx.success("Maintenance mode is now inactive.")


def setup(bot):
    bot.add_cog(Misc(bot))
