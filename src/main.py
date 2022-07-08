import os
import sys
import traceback
from datetime import datetime
import aiohttp
import discord
import dotenv
from discord.ext import commands, tasks

from config import AUTHORIZED, COLORS, EMOTES
from resources.mongoFunctions import database

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
        self.changing_presence.start()

        for event in os.listdir("src/events"):
            if event.endswith(".py"):
                try:
                    self.load_extension(f"events.{event[:-3]}")
                    print(f"✅ Loaded event: {event}")
                except Exception as e:
                    print(f"❌ Failed to load event: {event}: {e}")

        for command in os.listdir("src/cogs"):
            if command.endswith(".py"):
                try:
                    self.load_extension(f"cogs.{command[:-3]}")
                    print(f"✅ Loaded cog: {command}")
                except Exception as e:
                    print(f"❌ Failed to load cog: {command}: {e}")

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
                title=f"{EMOTES['error']} Something Went Wrong | Event: {event}", color=COLORS["error"], timestamp=datetime.utcnow())
            embed.description = f"```py\n{tb}```"
            await webhook.send(embed=embed)

    @tasks.loop(minutes=5.0)
    async def changing_presence(self):
        presences = [{"type": discord.ActivityType.listening,
                      "status": "questions | blox.link"}, {"type": discord.ActivityType.watching,
                                                           "status": f"{len(self.users)} users | blox.link"}, {"type": discord.ActivityType.playing,
                                                                                                               "status": f"/tag send | blox.link"}]
        await self.change_presence(status=discord.Status.online, activity=discord.Activity(type=presences[self.presence_index]["type"], name=presences[self.presence_index]["status"]))
        print("✅ Changed presence to: " +
              presences[self.presence_index]["status"])
        self.presence_index += 1
        if self.presence_index >= len(presences):
            self.presence_index = 0

    @changing_presence.before_loop()
    async def before_changing_presence(self):
        await self.wait_until_ready()


bot = Bot()
bot.run(os.getenv("TOKEN"))
