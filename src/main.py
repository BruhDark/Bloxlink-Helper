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
        self.maintenance = False
        self.ready = False

        for event in os.listdir("src/events"):
            if event.endswith(".py"):
                try:
                    self.load_extension(f"events.{event[:-3]}", store=False)
                    print(f"✅ Loaded event: {event}")
                except Exception as e:
                    print(f"❌ Failed to load event: {event}: {e}")

        for cog in os.listdir("src/cogs"):
            if cog.endswith(".py"):
                try:
                    self.load_extension(f"cogs.{cog[:-3]}", store=False)
                    print(f"✅ Loaded cog: {cog}")
                except Exception as e:
                    print(f"❌ Failed to load cog: {cog}: {e}")
                    raise e

    async def on_interaction(self, interaction: discord.Interaction):
        if self.maintenance and interaction.user.id not in AUTHORIZED:
            await interaction.response.send_message(f"{emotes.error} I am on maintenance mode! We don't want to cause any errors until I am fully operational. Try again later.", ephemeral=True)
            return
        return await super().on_interaction(interaction)

    async def on_message(self, message: discord.Message):
        if self.maintenance and message.author.id not in AUTHORIZED:
            return
        return await super().on_message(message)

    async def get_context(self, message: discord.Message, *, cls=CommandsContext):
        return await super().get_context(message, cls=cls)

    async def get_application_context(self, interaction: discord.Interaction, cls=ApplicationCommandsContext):
        return await super().get_application_context(interaction, cls=cls)

    async def on_connect(self):
        await self.sync_commands()
        print(f"🏓 Connected to Discord and registered slash commands.")

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


bot = Bot()
bot.run(os.getenv("TOKEN"))
