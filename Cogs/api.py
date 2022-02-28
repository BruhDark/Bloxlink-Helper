import discord
from discord.ext import commands
import requests
from config import EMOTES, LINKS

class ApiCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def api(self, ctx: discord.ApplicationContext, query: str):

        url = f"https://api.blox.link/v1/user/{query}"
        response = requests.get(url)

        embed = discord.Embed(description=f"Sent request to {url}.\n\n**Response**\n```json\n{response.text}```")
        embed.set_author(icon_url=LINKS["success"], name="Successfully sent request")

        await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(ApiCommand(bot))