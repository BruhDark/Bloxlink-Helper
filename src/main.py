import os
from Resources.mongoFunctions import database
import discord
from discord.ext import commands
from config import AUTHORIZED, COLORS
import dotenv
import sys
import aiohttp
import traceback

dotenv.load_dotenv()

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

        for event in os.listdir("src/Events"):
            if event.endswith(".py"):
                self.load_extension(f"Events.{event[:-3]}")
                print(f"Loaded event: {event}")

        for command in os.listdir("src/Cogs"):
            if command.endswith(".py"):
                self.load_extension(f"Cogs.{command[:-3]}")
                print(f"Loaded cog: {command}")

    async def is_owner(self, user: discord.User):
        if user.id in AUTHORIZED:
            return True

        return await super().is_owner(user)

    async def on_error(self, event_method, *args, **kwargs):
        async with aiohttp.ClientSession() as session:
            url = os.getenv("WEBHOOK_URL")
            webhook = discord.Webhook.from_url(url, session=session)
            tb = ''.join(traceback.format_tb(sys.exc_info()[2]))
            tb = tb + "\n" + str(sys.exc_info()[1])

            embed = discord.Embed(title="Something Went Wrong", color=COLORS["error"])
            embed.description = f"```py\n{tb}```"
            await webhook.send(embed=embed)

bot = Bot()
bot.run(os.getenv("TOKEN"))