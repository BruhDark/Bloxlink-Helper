import datetime
import os

import discord
import pandas as pd
from discord import Option, slash_command
from discord.ext import commands

from config import colors
from resources.CheckFailure import is_blacklisted, is_staff
from resources.context import ApplicationCommandsContext
from resources.mongoFunctions import find_one, return_all
from resources.paginator import CustomPaginator


class ExportStats(discord.ui.View):
    def __init__(self, rating: list):
        super().__init__()
        self.rating = rating

    @discord.ui.button(label="Export as CSV file", emoji="<:box:987447660510334976>", style=discord.ButtonStyle.blurple)
    async def export_callback(self, button: discord.Button, interaction: discord.Interaction):

        users = [rate['user'] for rate in self.rating]
        dates = [rate['date'] for rate in self.rating]
        number = [rate['rating'] for rate in self.rating]
        feedback = []
        for rate in self.rating:
            try:
                feedback.append(rate["feedback"])
            except KeyError:
                feedback.append("None")

        data = {"user": users, "date": dates,
                "rating": number, "feedback": feedback}

        df = pd.DataFrame(data)
        df.to_csv("stats.csv")

        await interaction.response.send_message(file=discord.File("stats.csv", "stats.csv"), ephemeral=True)
        os.remove("stats.csv")


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

    async def parse_rating_message(self, rating: list, detailed: bool = True):
        parsed_messages = []

        rating.sort(key=lambda rate: rate["rating"], reverse=True)

        if detailed:

            for rate in rating:
                try:
                    print(rate)
                    parsed_messages.append(
                        f"<t:{rate['date']}:D> {await self.return_stars(int(rate['rating']))} -> <@{rate['user']}>\n<:reply:1015305389249671178> **Feedback:** {rate['feedback']}")
                except:
                    parsed_messages.append(
                        f"<t:{rate['date']}:D> {await self.return_stars(int(rate['rating']))} -> <@{rate['user']}>")

        else:
            for rate in rating:
                pass

        return parsed_messages

    async def get_ranking(self, rating: list):
        first_rating = 0
        first_user = None
        second_rating = 0
        second_user = None
        third_rating = 0
        third_user = None

        users = {}
        for rate in rating:
            try:
                users[str(rate["user"])] += int(rate["rating"])

            except KeyError:
                users[str(rate["user"])] = int(rate["rating"])

        print(users)

        for index, (key, value) in enumerate(users.items()):
            if int(value) > int(first_rating):
                first_rating = value
                first_user = int(key)

            if int(second_rating) < int(value) < int(first_rating):
                second_rating = value
                second_user = int(key)

            if int(third_rating) < int(value) < int(second_rating):
                third_rating = value
                third_user = int(key)

        first = f"🥇 <@{first_user}> (`{first_user}`): {first_rating} Stars" if first_user is not None else "🥇 No one yet"
        second = f"🥈 <@{second_user}> (`{second_user}`): {second_rating} Stars" if second_user is not None else "🥈 No one yet"
        third = f"🥉 <@{third_user}> (`{third_user}`): {third_rating} Stars" if third_user is not None else "🥉 No one yet"

        ranking = f"{first}\n{second}\n{third}"
        return ranking

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

        await ctx.defer(ephemeral=True) if detailed else await ctx.defer()

        rating = await return_all("rating")
        embed = discord.Embed(
            color=colors.info, timestamp=discord.utils.utcnow())

        if detailed:
            if not discord.utils.get(ctx.guild.roles, id=595733840849534982) in ctx.author.roles and not await self.bot.is_owner(ctx.author):
                await ctx.error("Only Community Managers are able to view detailed stats.", ephemeral=True)
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
                        embed.set_author(
                            name=f"{user.name}#{user.discriminator}'s Rating Stats", icon_url=user.display_avatar.url)
                        embed.timestamp = datetime.datetime.utcnow()
                        embed.set_footer(
                            text=f"{await self.return_average(rating)}/5 Average Rating Stars")

                    paginator = CustomPaginator(
                        pages=embeds, disable_on_timeout=True, timeout=120, show_disabled=False, custom_view=ExportStats(rating))

                    await paginator.respond(ctx.interaction, ephemeral=True)

                else:
                    nrating = await self.parse_rating_message(rating)
                    message = await self.parse_embeds(nrating)
                    for embed in message:
                        embed.set_author(
                            name=f"All Team Rating Stats", icon_url=ctx.guild.icon.url)
                        embed.timestamp = datetime.datetime.utcnow()
                        embed.set_footer(
                            text=f"{await self.return_average(rating)}/5 Average Rating Stars")

                    paginator = CustomPaginator(
                        pages=message, disable_on_timeout=True, timeout=120, show_disabled=False, custom_view=ExportStats(rating))

                    await paginator.respond(ctx.interaction, ephemeral=True)

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

                    view = ExportStats(rating)
                    await ctx.respond(embed=embed, view=view, ephemeral=True)

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

                    view = ExportStats(rating)
                    await ctx.respond(embed=embed, view=view, ephemeral=True)

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
                    await ctx.respond(embed=embed, ephemeral=True)

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
                    await ctx.respond(embed=embed, ephemeral=True)

        else:
            embed = discord.Embed(
                color=colors.info, timestamp=datetime.datetime.utcnow())
            if date == "all time":
                if user:
                    nrating = [
                        rate for rate in rating if rate["user"] == user.id]

                    if len(nrating) == 0:
                        await ctx.error("This user has not received any rating yet!")
                        return

                    message = self.parse_rating_message(nrating)
                    embed.description = f":star: Average Stars: {await self.return_average(rating)}/5."
                    embed.set_author(
                        name=f"{user.name}#{user.discriminator}'s Average Stats", icon_url=user.display_avatar.url)
                    await ctx.respond(embed=embed)

                else:
                    if len(rating) == 0:
                        await ctx.error("No rating received yet!")
                        return

                    ranking = await self.get_ranking(rating)

                    embed.description = ranking
                    embed.set_footer(
                        text=f"{await self.return_average(rating)}/5 Average Stars")
                    embed.set_author(
                        name=f"All Team Rating Ranking", icon_url=ctx.guild.icon.url)

                    await ctx.respond(embed=embed)

            elif date == "month":
                if user:
                    nrating = await self.check_month(rating, user)

                    if len(nrating) == 0:
                        await ctx.error("This user has not received any rating yet!")
                        return

                    message = await self.get_ranking(nrating)
                    embed.description = f":star: Average Stars: {await self.return_average(rating)}/5."
                    embed.set_author(
                        name=f"{user.name}#{user.discriminator}'s This Month Rating Stats", icon_url=user.display_avatar.url)
                    await ctx.respond(embed=embed)

                else:
                    rating = await self.check_month(rating)
                    if len(rating) == 0:
                        await ctx.error("No rating received yet!")
                        return

                    ranking = await self.get_ranking(rating)

                    embed.description = ranking
                    embed.set_footer(
                        text=f"{await self.return_average(rating)}/5 Average Stars")
                    embed.set_author(
                        name=f"All Team Month Rating Ranking", icon_url=ctx.guild.icon.url)

                    await ctx.respond(embed=embed)

            elif date == "today":
                if user:
                    nrating = await self.check_today(rating, user)

                    if len(nrating) == 0:
                        await ctx.error("This user has not received any rating yet!")
                        return

                    message = self.get_ranking(nrating)
                    embed.description = f":star: Average Stars: {await self.return_average(rating)}/5."
                    embed.set_author(
                        name=f"{user.name}#{user.discriminator}'s Today Average Stats", icon_url=user.display_avatar.url)
                    await ctx.respond(embed=embed)

                else:
                    rating = await self.check_today(rating)
                    if len(rating) == 0:
                        await ctx.error("No rating received yet!")
                        return

                    ranking = await self.get_ranking(rating)

                    embed.description = ranking
                    embed.set_footer(
                        text=f"{await self.return_average(rating)}/5 Average Stars")
                    embed.set_author(
                        name=f"All Team Today's Ranking", icon_url=ctx.guild.icon.url)

                    await ctx.respond(embed=embed)


def setup(bot):
    bot.add_cog(Rating(bot))
