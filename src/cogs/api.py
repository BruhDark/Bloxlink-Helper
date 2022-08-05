import discord
import aiohttp
import datetime
from config import colors, emotes, links
from discord.ext import commands


class ApiCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.guild_only()
    async def api(self, ctx: discord.ApplicationContext, query: str):

        url = f"https://v3.blox.link/developer/discord/{query}"
        headers = {
            "api-key": "657809d4-8daa-4658-bf83-0084d643c88b2b10def8-b27e-4713-a17b-02e5e562aa100c8ee099-a366-4e71-bbdb-946f826646d8"}

        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as response:
                data = await response.text()
                headers = response.headers
                quota = headers["quota-remaining"]

                embed = discord.Embed(timestamp=datetime.datetime.utcnow(
                ), description=f"Sent request to {url}.\n\n**Response**\n```json\n{data}```", color=colors.info)
                embed.set_author(icon_url=links.success,
                                 name="Successfully sent request")
                embed.set_footer(text=f"Quota remaining: {quota} requests")

                await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(ApiCommand(bot))
