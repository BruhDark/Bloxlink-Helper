import os
from datetime import datetime

import aiohttp
import discord
from discord.ext import commands

from resources.CheckFailure import is_blacklisted, is_staff
from config import colors, emotes, links


class ApiCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.group(invoke_without_command=True)
    @is_staff()
    async def api(self, ctx: commands.Context):
        """API Commands"""
        embed = discord.Embed(color=colors.info)
        embed.title = f"{emotes.bloxlink} This command was updated!"

        embed.description = "You must either specify `v3` or `v4` as the first command argument and then the ID. If " \
                            "you want to make a request to the V4 global API, specify `v4`. If you want to make a " \
                            "request to the V3 API, specify `v3`"

        embed.timestamp = datetime.utcnow()
        embed.set_footer(
            text="V3 subcommand will be removed when the endpoint does")
        await ctx.reply(embed=embed, mention_author=False)

    @api.command(name="v3")
    @commands.cooldown(1, 10, commands.BucketType.user)
    @commands.guild_only()
    @is_blacklisted()
    @is_staff()
    async def apiv3(self, ctx: commands.Context, discord_id: str):
        headers = {
            "api-key": os.getenv("API_KEY")
        }

        url = f"https://v3.blox.link/developer/discord/{discord_id}"
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as response:
                data = await response.json()
                headers = response.headers
                try:
                    quota = headers["quota-remaining"]
                except KeyError:
                    quota = "?"

                embed = discord.Embed(timestamp=datetime.utcnow(
                ), description=f"Sent request to {url}.\n\n**Response**\n```json\n{data}```", color=colors.info)
                embed.set_author(icon_url=links.success,
                                 name="Successfully sent request")
                embed.set_footer(text=f"{quota} requests remaining")

        await ctx.reply(embed=embed, mention_author=False)

    @api.command(name="v4")
    @commands.cooldown(1, 10, commands.BucketType.user)
    @commands.guild_only()
    @is_blacklisted()
    @is_staff()
    async def apiv4(self, ctx: commands.Context, discord_id: str):
        headers = {
            "Authorization": os.getenv("APIV4_KEY")
        }

        url = f"https://api.blox.link/v4/public/discord-to-roblox/{discord_id}"
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as response:
                data = await response.json()
                headers = response.headers
                try:
                    quota = headers["quota-remaining"]
                except KeyError:
                    quota = "?"

                embed = discord.Embed(timestamp=datetime.utcnow(
                ), description=f"Sent request to {url}.\n\n**Response**\n```json\n{data}```", color=colors.info)
                embed.set_author(icon_url=links.success,
                                 name="Successfully sent request")
                embed.set_footer(text=f"{quota} requests remaining")

        await ctx.reply(embed=embed, mention_author=False)

    @commands.user_command(name="Send API request")
    @commands.cooldown(1, 10, commands.BucketType.user)
    @is_blacklisted()
    @is_staff()
    async def api_user(self, ctx: discord.ApplicationContext, member: discord.Member):

        headers = {
            "Authorization": os.getenv("APIV4_KEY")}
        url = f"https://api.blox.link/v4/public/discord/{member.id}"
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as resp:
                data = await resp.json()
                headers = resp.headers
                try:
                    quota = headers["quota-remaining"]
                except KeyError:
                    quota = "?"

                embed = discord.Embed(timestamp=datetime.utcnow(
                ), description=f"Sent request to {url}.\n\n**Response**\n```json\n{data}```", color=colors.info)
                embed.set_author(icon_url=links.success,
                                 name="Successfully sent request")
                embed.set_footer(text=f"{quota} requests remaining")

        await ctx.respond(embed=embed, ephemeral=True)


def setup(bot):
    bot.add_cog(ApiCommand(bot))
