import os
import sys
import traceback
from datetime import datetime
import aiohttp
import discord
import dotenv
from discord.ext import commands, tasks
from resources.context import CommandsContext, ApplicationCommandsContext

from config import AUTHORIZED, colors, emotes
from resources.mongoFunctions import database, find_tag

try:
    dotenv.load_dotenv()
except:
    pass


class Bot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix=commands.when_mentioned_or("."),
                         intents=discord.Intents.all(),
                         strip_after_prefix=True,
                         allowed_mentions=discord.AllowedMentions(
            users=True,
            everyone=False,
            roles=False,
            replied_user=True,
        ),
            help_command=None)
        self.database = database
        self.presence_index = 0
        self.ready = False
        self.presences = [{"type": discord.ActivityType.listening,
                           "status": "questions | blox.link"}, {"type": discord.ActivityType.watching,
                                                                "status": f"{len(self.users)} users | blox.link"}, {"type": discord.ActivityType.playing,
                                                                                                                    "status": f"/tag send | blox.link"}, {"type": discord.ActivityType.watching, "status": f"tutorials | blox.link/tutorials"}]
        self.changing_presence.start()
        self.post_faq.start()

        for event in os.listdir("src/events"):
            if event.endswith(".py"):
                try:
                    self.load_extension(f"events.{event[:-3]}", store=False)
                    print(f"✅ Loaded event: {event}")
                except Exception as e:
                    print(f"❌ Failed to load event: {event}: {e}")

        for command in os.listdir("src/cogs"):
            if command.endswith(".py"):
                try:
                    self.load_extension(f"cogs.{command[:-3]}", store=False)
                    print(f"✅ Loaded cog: {command}")
                except Exception as e:
                    print(f"❌ Failed to load cog: {command}: {e}")
                    raise e

    async def get_context(self, message: discord.Message, *, cls=CommandsContext):
        return await super().get_context(message, cls=cls)

    async def get_application_context(self, interaction: discord.Interaction, cls=ApplicationCommandsContext):
        return await super().get_application_context(interaction, cls=cls)

    async def on_connect(self):
        await self.sync_commands()
        print(f":ping_pong: Connected to Discord and registered slash commands.")

    async def is_owner(self, user: discord.User):
        if user.id in AUTHORIZED:
            return True
        return await super().is_owner(user)

    async def on_error(self, event: str, *args, **kwargs):
        async with aiohttp.ClientSession() as session:
            url = os.getenv("WEBHOOK_URL")
            webhook = discord.Webhook.from_url(url, session=session)
            tb = ''.join(traceback.format_tb(sys.exc_info()[2]))
            tb = tb + "\n" + str(sys.exc_info()[1])

            embed = discord.Embed(
                title=f"{emotes.error} Something Went Wrong | Event: {event}", color=colors.error, timestamp=datetime.utcnow())
            embed.description = f"```py\n{tb}```"
            await webhook.send(embed=embed)

    @tasks.loop(seconds=60*5)  # 5 minutes
    async def changing_presence(self):

        await self.change_presence(status=discord.Status.online, activity=discord.Activity(type=self.presences[self.presence_index]["type"], name=self.presences[self.presence_index]["status"]))
        print("✅ Changed presence to: " +
              self.presences[self.presence_index]["status"])
        self.presence_index += 1
        if self.presence_index >= len(self.presences):
            self.presence_index = 0

    @changing_presence.before_loop
    async def before_changing_presence(self):
        await self.wait_until_ready()

    @tasks.loop(minutes=30)
    async def post_faq(self):

        guild = self.get_guild(372036754078826496)
        channel = guild.get_channel(372181186816245770)
        channel = await guild.fetch_channel(372181186816245770) if channel is None else channel
        last_message = channel.last_message

        if last_message.author == self.user.id:
            return

        faq = await find_tag("faq")
        await channel.send(faq)

    @post_faq.before_loop
    async def before_post_faq(self):
        await self.wait_until_ready()


bot = Bot()
bot.run(os.getenv("TOKEN"))
