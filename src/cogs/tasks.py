import discord
from discord.ext import commands, tasks
from config import emotes
from resources.mongoFunctions import find_tag


class Tasks(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot
        self.bot.changing_presence = self.changing_presence
        self.bot.post_faq = self.post_faq
        self.presence_index = 0
        self.last_message_sent = None

        self.changing_presence.start()
        self.post_faq.start()

    @tasks.loop(seconds=60*5)  # 5 minutes
    async def changing_presence(self):

        presences = [{"type": discord.ActivityType.listening,
                      "status": "questions | blox.link"}, {"type": discord.ActivityType.watching,
                                                           "status": f"{len(self.users)} users | blox.link"}, {"type": discord.ActivityType.playing,
                                                                                                               "status": f"/tag send | blox.link"}, {"type": discord.ActivityType.watching, "status": f"tutorials | blox.link/tutorials"},
                     {"type": discord.ActivityType.listening, "status": "Taylor Swift's songs"}]

        await self.bot.change_presence(activity=discord.Activity(type=presences[self.presence_index]["type"], name=presences[self.presence_index]["status"]))
        print("✅ Changed presence to: " +
              presences[self.presence_index]["status"])

        self.presence_index += 1

        if self.presence_index >= len(presences):
            self.presence_index = 0

    @changing_presence.before_loop
    async def before_changing_presence(self):
        await self.bot.wait_until_ready()

    @tasks.loop(minutes=30)
    async def post_faq(self):
        try:

            guild = self.bot.get_guild(372036754078826496)  # Bloxlink HQ
            # guild = self.get_guild(881968885279117342)  # Helper HQ
            channel = discord.utils.get(guild.channels, name="support")
            channel = await guild.fetch_channel(372181186816245770) if channel is None else channel
            last_message = channel.last_message
            last_message = await channel.fetch_message(channel.last_message_id) if last_message is None else last_message

            if last_message.author.id == self.bot.user.id:
                return

            tag = await find_tag("faq")

            view = discord.ui.View()
            view.add_item(discord.ui.Button(
                label="This is an automated message", disabled=True))

            try:
                await self.last_message_sent.delete()
            except:
                pass
            message = await channel.send(content=tag["content"], view=view)

            self.last_message_sent = message

        except Exception as e:
            print("Failed to post:")
            print(e)

    @post_faq.before_loop
    async def before_post_faq(self):
        await self.bot.wait_until_ready()


def setup(bot):
    bot.add_cog(Tasks(bot))
