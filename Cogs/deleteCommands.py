import asyncio

import discord
from discord.ext import commands


class IgnoredCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):

        possibleCommands = ("!verify", "!getroles", "!settings",
                            "!!verify", "!!getroles", "!!settings")
        channels = [372181186816245770, 771034042829242418, 372036754078826499]
        ignoredRoles = [889927613580189716]

        if message.content.startswith(possibleCommands) and message.channel.id in channels and ignoredRoles not in message.author.roles:

            await message.delete
            await message.channel.send(f"{message.author.mention} Commands are only meant to be ran in <#372181138002935819>! Also consider using the slash command version of it.")


def setup(bot):
    pass
