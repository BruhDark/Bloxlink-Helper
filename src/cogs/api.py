import discord
import aiohttp
import datetime
from config import colors, emotes, links
from discord.ext import commands
import os


class ApiCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.cooldown(1, 10, commands.BucketType.user)
    @commands.guild_only()
    async def api(self, ctx: discord.ApplicationContext, *, query: str):
        verified = discord.utils.get(ctx.guild.roles, name="Verified")
        if verified not in ctx.author.roles:
            embed = discord.Embed(
                description=f"{emotes.error} You must be verified with Bloxlink to use this command", color=colors.error)
            await ctx.send(embed=embed)
            return

        headers = {
            "api-key": os.getenv("API_KEY")}

        query = query.lower()

        if query.startswith("reverse"):
            query = query.split(" ")
            print(query)
            query = query[1]
            url = f"https://v3.blox.link/developer/roblox/{query}"
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers) as resp:
                    data = await resp.json()
                    headers = resp.headers
                    try:
                        quota = headers["quota-remaining"]
                    except:
                        quota = "?"

                    embed = discord.Embed(timestamp=datetime.datetime.utcnow(
                    ), description=f"Sent request to {url}.\n\n**Response**\n```json\n{data}```", color=colors.info)
                    embed.set_author(icon_url=links.success,
                                     name="Successfully sent request")
                    embed.set_footer(text=f"{quota} requests remaining")

                    await ctx.send(embed=embed)

        else:

            url = f"https://v3.blox.link/developer/discord/{query}"
            url = url.replace(
                "?guildid", "?guildId") if "?guildid" in url else url
            headers = {
                "api-key": os.getenv("API_KEY")}

            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers) as response:
                    data = await response.text()
                    headers = response.headers
                    try:
                        quota = headers["quota-remaining"]
                    except:
                        quota = "?"

                    embed = discord.Embed(timestamp=datetime.datetime.utcnow(
                    ), description=f"Sent request to {url}.\n\n**Response**\n```json\n{data}```", color=colors.info)
                    embed.set_author(icon_url=links.success,
                                     name="Successfully sent request")
                    embed.set_footer(text=f"{quota} requests remaining")

                    await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(ApiCommand(bot))
