import discord
from discord.ext import commands
import pymongo
import os

client = pymongo.MongoClient("mongodb+srv://bloxlinkHelper:ZR8otSoEzWCuGLye@cluster0.gee6w.mongodb.net/")
database = client["bloxlinkHelper"]

class Bot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix=commands.when_mentioned_or("."), 
        intents=discord.Intents.all(),
        strip_after_prefix=True,
        debug_guilds=[881968885279117342, 789699000047370261],
        allowed_mentions=discord.AllowedMentions(
        users=True,         # Whether to ping individual user @mentions
        everyone=False,      # Whether to ping @everyone or @here mentions
        roles=False,         # Whether to ping role @mentions
        replied_user=True,  # Whether to ping on replies to messages
        ),
        help_command=None)
        self.database = database
    
        for event in os.listdir("Events"):
         if event.endswith(".py"):
             self.load_extension(f"Events.{event[:-3]}")
             print(f"Loaded event: {event}")
    
        for command in os.listdir("Cogs"):
         if command.endswith(".py"):
             self.load_extension(f"Cogs.{command[:-3]}")
             print(f"Loaded cog: {command}")

        try:
         self.load_extension("jishaku")
         print("Loaded extension: jishaku")

        except Exception as e:
         print("Could not load jishaku: {e}")

bot = Bot()
bot.run("OTQzMTUwMDcyODI3MzU1MTc3.Ygu29A.Lt7s9SDTz6wtIgUDosYbVDq3pTQ")