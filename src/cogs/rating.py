import datetime
import discord
from discord import ApplicationContext, Option, slash_command
from discord.ext import commands
from resources.context import ApplicationCommandsContext
from resources.mongoFunctions import return_all, find_one
from config import colors, links
import time
from quickchart import QuickChart
from resources.CheckFailure import is_blacklisted, is_staff


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

    def return_average(self, rate_list: list):
        rating = [rate['rating'] for rate in rate_list]

        average = 0
        for rate in rating:
            average += int(rate)

        return round(average / len(rating), 2)

    def check_today(self, rating: list, user: discord.Member = None):
        parsed_rating = []

        if user:
            for rate in rating:
                timestamp = datetime.datetime.fromtimestamp(rate["date"])
                today = datetime.datetime.utcnow()
                timestamp, today = timestamp.replace(hour=0, minute=0, second=0, microsecond=0), today.replace(
                    hour=0, minute=0, second=0, microsecond=0)

                if timestamp == today and rate["user"] == user.id:
                    parsed_rating.append(rate)

            return parsed_rating

        else:
            for rate in rating:
                timestamp = datetime.datetime.fromtimestamp(rate["date"])
                today = datetime.datetime.utcnow()
                timestamp, today = timestamp.replace(hour=0, minute=0, second=0, microsecond=0), today.replace(
                    hour=0, minute=0, second=0, microsecond=0)

                if timestamp == today:
                    parsed_rating.append(rate)

            return parsed_rating

    @slash_command(description="Get a staff member rating stats")
    @is_staff()
    @is_blacklisted()
    async def rating(self, ctx: ApplicationCommandsContext, date: Option(str, "Rating date", choices=["all time", "today", "month"]), user: Option(discord.Member, "A staff member to get rating of", required=False) = None):

        rating = await return_all("rating")
        embed = discord.Embed(color=colors.info)
        if date == "all time":
            if user:
                rating = [rate for rate in rating if rate["user"] == user.id]

                if len(rating) == 0:
                    await ctx.error("This user hasn't received any rating yet!")
                    return

                nrating = [
                    f"<t:{rate['date']}:D> {self.return_stars(int(rate['rating']))}" for rate in rating]

                embed.description = "\n".join(nrating)
                embed.set_author(
                    name=f"{user.name}#{user.discriminator}'s Rating Stats", icon_url=user.display_avatar.url)
                embed.timestamp = datetime.datetime.utcnow()
                embed.set_footer(
                    text=f"{self.return_average(rating)}/5 Average Rating Stars")
                await ctx.respond(embed=embed)

            else:
                nrating = [
                    f"<t:{rate['date']}:D> {self.return_stars(int(rate['rating']))} -> <@{rate['user']}> (`{rate['user']}`)" for rate in rating]

                embed.description = "\n".join(nrating)
                embed.set_author(
                    name=f"All Team Rating Stats", icon_url=ctx.guild.icon.url)
                embed.timestamp = datetime.datetime.utcnow()
                embed.set_footer(
                    text=f"{self.return_average(rating)}/5 Average Rating Stars")
                await ctx.respond(embed=embed)

        elif date == "today":
            if user:
                rating = self.check_today(rating)

                if len(rating) == 0:
                    await ctx.error("This user hasn't received any rating today!")
                    return

                nrating = [
                    f"<t:{rate['date']}:D> {self.return_stars(int(rate['rating']))}" for rate in rating]

                embed.description = "\n".join(nrating)
                embed.set_author(
                    name=f"{user.name}#{user.discriminator}'s Today Rating Stats", icon_url=user.display_avatar.url)
                embed.timestamp = datetime.datetime.utcnow()
                embed.set_footer(
                    text=f"{self.return_average(rating)}/5 Average Rating Stars")
                await ctx.respond(embed=embed)

            else:
                rating = self.check_today(rating)
                if len(rating) == 0:
                    await ctx.error("No rating received today yet.")
                    return

                nrating = [
                    f"<t:{rate['date']}:D> {self.return_stars(int(rate['rating']))} -> <@{rate['user']}> (`{rate['user']}`)" for rate in rating]

                embed.description = "\n".join(nrating)
                embed.set_author(
                    name=f"All Team Today Rating Stats", icon_url=ctx.guild.icon.url)
                embed.timestamp = datetime.datetime.utcnow()
                embed.set_footer(
                    text=f"{self.return_average(rating)}/5 Average Rating Stars")
                await ctx.respond(embed=embed)

        elif date == "month":
            await ctx.error("This option is still in development")

        else:
            await ctx.error("Not a valid option selected", ephemeral=True)


def setup(bot):
    bot.add_cog(Rating(bot))
