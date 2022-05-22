import os
from time import sleep
from Resources.mongoFunctions import database
import discord
from discord.ext import commands
from config import AUTHORIZED

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
            help_command=None,
            debug_guilds=[881968885279117342])
        self.database = database

        for event in os.listdir("Events"):
            if event.endswith(".py"):
                self.load_extension(f"Events.{event[:-3]}")
                print(f"Loaded event: {event}")

        for command in os.listdir("Cogs"):
            if command.endswith(".py"):
                self.load_extension(f"Cogs.{command[:-3]}")
                print(f"Loaded cog: {command}")

    async def is_owner(self, user: discord.User):
        if user.id in AUTHORIZED:
            return True

        return await super().is_owner(user)


bot = Bot()
bot.run("OTEyODQ2MzU5Nzg5NDYxNTI1.YZ14bA.rDkuSJUXuvXvwhzXMoKICAkGxjI")
# OTQzMTUwMDcyODI3MzU1MTc3.Ygu29A.mVwKQoVxIHCI5ztBt-rBb6wlsug