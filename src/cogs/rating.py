import datetime
import discord
from discord import ApplicationContext, Option, slash_command
from discord.ext import commands
from resources.mongoFunctions import return_all, find_one
from config import colors, links
import time
from quickchart import QuickChart


class Rating(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot

    def build_embed(self, user: discord.Member, title, description):
        embed = discord.Embed(
            title=title, description=description, color=colors.info)

        embed.timestamp = datetime.datetime.utcnow()
        embed.set_author(name=user, icon_url=user.avatar.url)

        return embed

    def return_stars(self, starscount: int):
        stars = ""
        for i in range(starscount):
            stars += "⭐"
        return stars

    @slash_command()
    async def rating(self, ctx: ApplicationContext, date: Option(str, "Rating date", choices=["all time", "today", "monthly"]), user: Option(discord.Member, "A staff member to get rating of", required=False) = None):

        rating = await return_all("rating")
        if date == "all time" and user:
            rating = [rate for rate in rating if rate["user"] == user.id]
            nrating = [
                f"<t:{rate['date']}:D> {self.return_stars(int(rate['rating']))}" for rate in rating]

            embed = self.build_embed(

                user, f"{user.name}'s rating", "\n".join(nrating))
            await ctx.respond(embed=embed)


def setup(bot):
    bot.add_cog(Rating(bot))
