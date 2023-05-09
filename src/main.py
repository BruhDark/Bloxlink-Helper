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
        self.presence_index = 0
        self.ready = False
        self.changing_presence.start()
        self.post_faq.start()
        self.last_message_sent = None
        self.maintenance = False

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
            await interaction.response.send_message(f"{emotes.error} I am on maintenance mode! We don't want to cause any errors until I am fully operational. Try again later.")
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

    @tasks.loop(seconds=60*5)  # 5 minutes
    async def changing_presence(self):

        presences = [{"type": discord.ActivityType.listening,
                      "status": "questions | blox.link"}, {"type": discord.ActivityType.watching,
                                                           "status": f"{len(self.users)} users | blox.link"}, {"type": discord.ActivityType.playing,
                                                                                                               "status": f"/tag send | blox.link"}, {"type": discord.ActivityType.watching, "status": f"tutorials | blox.link/tutorials"},
                     {"type": discord.ActivityType.listening, "status": "Taylor Swift's songs"}]

        await self.change_presence(status=discord.Status.online, activity=discord.Activity(type=presences[self.presence_index]["type"], name=presences[self.presence_index]["status"]))
        print("✅ Changed presence to: " +
              presences[self.presence_index]["status"])
        self.presence_index += 1
        if self.presence_index >= len(presences):
            self.presence_index = 0

    @changing_presence.before_loop
    async def before_changing_presence(self):
        await self.wait_until_ready()

    @tasks.loop(minutes=30)
    async def post_faq(self):
        try:

            guild = self.get_guild(372036754078826496)  # Bloxlink HQ
            # guild = self.get_guild(881968885279117342)  # Helper HQ
            channel = discord.utils.get(guild.channels, name="support")
            channel = await guild.fetch_channel(372181186816245770) if channel is None else channel
            last_message = channel.last_message
            last_message = await channel.fetch_message(channel.last_message_id) if last_message is None else last_message

            if last_message.author.id == self.user.id:
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
        await self.wait_until_ready()


bot = Bot()
bot.run(os.getenv("TOKEN"))
