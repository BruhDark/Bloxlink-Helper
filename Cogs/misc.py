import datetime

import discord
from discord.ext import commands
from config import COLORS, EMOTES, LINKS
from Resources.mongoFunctions import *


class Misc(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command()
    @commands.is_owner()
    async def blacklist(self, ctx: commands.Context, choice: str, user: discord.Member, *, reason: str = None):
        """Blacklist a user from using the bot."""

        user = user.id if type(user) == discord.Member else user

        if user.id == self.bot.user.id:
            x = EMOTES["error"]
            Embed = discord.Embed(
                description=f"{x} You can not blacklist me!", color=COLORS["error"])
            return await ctx.send(embed=Embed)

        if choice.lower() == "add":

            check = {"user": user}
            find = await find_one(check)

            if find:
                x = EMOTES["error"]
                Embed = discord.Embed(
                    description=f"{x} This user is already blacklisted!", color=COLORS["error"])
                return await ctx.send(embed=Embed)

            data = {"user": user.id, "reason": reason}
            item = await insert_one(data)

            embed = discord.Embed(
                color=COLORS["success"], timestamp=datetime.datetime.utcnow())
            embed.set_author(
                icon_url=LINKS["success"], name=f"Successfully blacklisted this user")

            user = self.bot.get_or_fetch_user(
                user) if type(user) == int else user
            embed.add_field(
                name="🕴️ User", value=f"{user.mention} ({user.id})")
            embed.add_field(name="📰 Reason", value=f"{reason}")

            embed.set_footer(text="Item ID: {}".format(item.inserted_id))

            await ctx.send(embed=embed)

        elif choice.lower() == "remove":

            check = {"user": user}
            find = await find_one(check)

            if not find:
                x = EMOTES["error"]
                Embed = discord.Embed(
                    description=f"{x} This user is not blacklisted!", color=COLORS["error"])
                return await ctx.send(embed=Embed)

            await delete_one(check)

            s = EMOTES["success2"]

            embed = discord.Embed(
                color=COLORS["success"], description=f"{s} Successfully removed this user from the blacklist.")

            await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Misc(bot))
