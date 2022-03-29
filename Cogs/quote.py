import asyncio
import re

import discord
from config import COLORS
from discord.ext import commands


class Quote(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):

        if message.author != self.bot.user:

            pattern = re.compile(
                "https://(?:ptb.|canary.)?discord.com/channels/(?P<server_id>[0-9]{17,20})/(?P<channel_id>[0-9]{17,20})/(?P<message_id>[0-9]{17,20})")

            found = re.search(pattern, message.content)

            if found:

                msg_id = int(found.group('message_id'))
                server_id = int(found.group("server_id"))
                channel_id = int(found.group("channel_id"))

                msg = discord.utils.get(self.bot.cached_messages, id=msg_id)
                msg = await discord.abc.Messageable.fetch_message(discord.utils.get(message.guild.channels, id=channel_id), msg_id) if msg is None else msg

                if msg:
                    await message.add_reaction("📦")

                    def check(reaction, user):
                        return user == message.author and str(reaction.emoji) == "📦"

                    try:
                        await self.bot.wait_for("reaction_add", timeout=15.0, check=check)

                    except asyncio.TimeoutError:
                        await message.remove_reaction("📦", self.bot.user)

                    else:
                        embed = discord.Embed(
                            title=f"Jump to message", url=f"https://discord.com/channels/{server_id}/{channel_id}/{msg_id}", description=msg.content, color=COLORS["info"], timestamp=msg.created_at)
                        embed.set_author(
                            name=f"{msg.author} in {msg.channel}", icon_url=msg.author.avatar.url)
                        embed.set_footer(
                            text=f"Quoted by: {message.author}", icon_url=message.author.display_avatar.url)
                        await message.channel.send(embed=embed)


def setup(bot):
    bot.add_cog(Quote(bot))
