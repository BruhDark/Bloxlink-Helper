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
from resources.paginator import CustomPaginator


class Rating(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot

    async def build_embed(self, user: discord.Member, title, description):
        embed = discord.Embed(
            title=title, description=description, color=colors.info)

        embed.timestamp = datetime.datetime.utcnow()
        embed.set_author(name=user, icon_url=user.avatar.url)

        return embed

    async def return_stars(self, starscount: int):
        stars = ""
        for i in range(starscount):
            stars += "⭐"
        return stars

    async def return_average(self, rate_list: list):
        rating = [rate['rating'] for rate in rate_list]

        average = 0
        for rate in rating:
            average += int(rate)

        return round(average / len(rating), 2)

    async def check_today(self, rating: list, user: discord.Member = None):
        parsed_rating = []

        if user:
            for rate in rating:
                timestamp = datetime.datetime.fromtimestamp(rate["date"])
                today = datetime.datetime.utcnow()

                if (timestamp.day, timestamp.month, timestamp.year) == (today.day, today.month, today.year) and rate["user"] == user.id:
                    parsed_rating.append(rate)

            return parsed_rating

        else:
            for rate in rating:
                timestamp = datetime.datetime.fromtimestamp(rate["date"])
                today = datetime.datetime.utcnow()

                if (timestamp.day, timestamp.month, timestamp.year) == (today.day, today.month, today.year):
                    parsed_rating.append(rate)

            return parsed_rating

    async def check_month(self, rating: list, user: discord.Member = None):
        parsed_rating = []

        if user:
            for rate in rating:
                timestamp = datetime.datetime.fromtimestamp(rate["date"])
                today = datetime.datetime.utcnow()

                if (timestamp.month, timestamp.year) == (today.month, today.year) and rate["user"] == user.id:
                    parsed_rating.append(rate)

            return parsed_rating

        else:
            for rate in rating:
                timestamp = datetime.datetime.fromtimestamp(rate["date"])
                today = datetime.datetime.utcnow()

                if (timestamp.month, timestamp.year) == (today.month, today.year):
                    parsed_rating.append(rate)

            return parsed_rating

    async def parse_rating_message(self, rating: list):
        parsed_messages = []

        rating.sort(key=lambda rate: rate["rating"], reverse=True)

        for rate in rating:
            if rate["rating"] <= 3:
                print(rate)
                parsed_messages.append(
                    f"<t:{rate['date']}:D> {await self.return_stars(int(rate['rating']))}\n<:reply:1015305389249671178> **Feedback:** {rate['feedback']}")
            else:
                parsed_messages.append(
                    f"<t:{rate['date']}:D> {await self.return_stars(int(rate['rating']))}")

        return parsed_messages

    async def get_ranking(self, rating: list):
        first = "None"
        second = "None"
        third = "None"

    async def parse_embeds(self, rating: list):
        embeds = []
        if len(rating) <= 5:
            rate = "\n".join(rating)
            embeds.append(discord.Embed(color=colors.info, description=rate))

            return embeds

        if len(rating) >= 6:
            rate = "\n".join(rating[:7])
            embeds.append(discord.Embed(color=colors.info, description=rate))

        if len(rating) >= 8:
            rate = "\n".join(rating[8:14])
            embeds.append(discord.Embed(color=colors.info, description=rate))

        if len(rating) >= 15:
            rate = "\n".join(rating[15:21])
            embeds.append(discord.Embed(color=colors.info, description=rate))

        if len(rating) >= 22:
            rate = "\n".join(rating[22:28])
            embeds.append(discord.Embed(color=colors.info, description=rate))

        return embeds

    @slash_command(description="Get a staff member rating stats")
    @is_staff()
    @is_blacklisted()
    async def rating(self, ctx: ApplicationCommandsContext, date: Option(str, "Rating date", choices=["all time", "today", "month"]), user: Option(discord.Member, "A staff member to get rating of", required=False) = None, detailed: bool = False):

        await ctx.defer()

        rating = await return_all("rating")
        embed = discord.Embed(color=colors.info)

        if detailed:
            if not discord.utils.get(ctx.guild.roles, name="Community Manager") in ctx.author.roles or not await self.bot.is_owner(ctx.author):
                await ctx.error("Only Community Managers are able to view detailed stats.")
                return

            if date == "all time":
                if user:
                    rating = [
                        rate for rate in rating if rate["user"] == user.id]

                    if len(rating) == 0:
                        await ctx.error("This user hasn't received any rating yet!")
                        return

                    nrating = await self.parse_rating_message(rating)
                    embeds = await self.parse_embeds(nrating)
                    for embed in embeds:
                        embed.description = "\n".join(nrating)
                        embed.set_author(
                            name=f"{user.name}#{user.discriminator}'s Rating Stats", icon_url=user.display_avatar.url)
                        embed.timestamp = datetime.datetime.utcnow()
                        embed.set_footer(
                            text=f"{await self.return_average(rating)}/5 Average Rating Stars")

                    paginator = CustomPaginator(pages=embeds)
                    await paginator.respond(ctx.interaction)

                else:
                    nrating = await self.parse_rating_message(rating)

                    embed.description = "\n".join(nrating)
                    embed.set_author(
                        name=f"All Team Rating Stats", icon_url=ctx.guild.icon.url)
                    embed.timestamp = datetime.datetime.utcnow()
                    embed.set_footer(
                        text=f"{await self.return_average(rating)}/5 Average Rating Stars")
                    await ctx.respond(embed=embed)

            elif date == "today":
                if user:
                    rating = await self.check_today(rating, user)

                    if len(rating) == 0:
                        await ctx.error("This user hasn't received any rating today!")
                        return

                    nrating = [
                        f"<t:{rate['date']}:D> {await self.return_stars(int(rate['rating']))}" for rate in rating]

                    embed.description = "\n".join(nrating)
                    embed.set_author(
                        name=f"{user.name}#{user.discriminator}'s Today Rating Stats", icon_url=user.display_avatar.url)
                    embed.timestamp = datetime.datetime.utcnow()
                    embed.set_footer(
                        text=f"{await self.return_average(rating)}/5 Average Rating Stars")
                    await ctx.respond(embed=embed)

                else:
                    rating = await self.check_today(rating)
                    if len(rating) == 0:
                        await ctx.error("No rating received today yet.")
                        return

                    nrating = await self.parse_rating_message(rating)

                    embed.description = "\n".join(nrating)
                    embed.set_author(
                        name=f"All Team Today Rating Stats", icon_url=ctx.guild.icon.url)
                    embed.timestamp = datetime.datetime.utcnow()
                    embed.set_footer(
                        text=f"{await self.return_average(rating)}/5 Average Rating Stars")
                    await ctx.respond(embed=embed)

            elif date == "month":
                if user:
                    rating = await self.check_month(rating, user)

                    if len(rating) == 0:
                        await ctx.error("This user hasn't received any rating this month!")
                        return

                    nrating = await self.parse_rating_message(rating)

                    embed.description = "\n".join(nrating)
                    embed.set_author(
                        name=f"{user.name}#{user.discriminator}'s This Month Rating Stats", icon_url=user.display_avatar.url)
                    embed.timestamp = datetime.datetime.utcnow()
                    embed.set_footer(
                        text=f"{await self.return_average(rating)}/5 Average Rating Stars")
                    await ctx.respond(embed=embed)

                else:
                    rating = await self.check_month(rating)
                    if len(rating) == 0:
                        await ctx.error("No rating received this month.")
                        return

                    nrating = await self.parse_rating_message(rating)

                    embed.description = "\n".join(nrating)
                    embed.set_author(
                        name=f"All Team Month Rating Stats", icon_url=ctx.guild.icon.url)
                    embed.timestamp = datetime.datetime.utcnow()
                    embed.set_footer(
                        text=f"{await self.return_average(rating)}/5 Average Rating Stars")
                    await ctx.respond(embed=embed)

        else:
            pass


def setup(bot):
    bot.add_cog(Rating(bot))
