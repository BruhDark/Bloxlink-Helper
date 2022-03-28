import discord
from discord.ext import commands
import re

class Suggestions(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):

        pattern = re.compile("(S|s)(?P<post>\d+)")
        find = re.search(pattern, message.content)

        if find:
            post = find.group("post")
            await message.channel.send(f"https://feedback.blox.link/posts/{post}")