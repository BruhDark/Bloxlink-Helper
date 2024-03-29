import asyncio
import discord
from discord import ButtonStyle
import time
from resources.mongoFunctions import insert_one
from config import emotes

RATE_OPTIONS = [
    discord.SelectOption(label="⭐⭐⭐⭐⭐", value="5",
                         description="The support provided was the best."),
    discord.SelectOption(label="⭐⭐⭐⭐", value="4",
                         description="The support provided was very good."),
    discord.SelectOption(label="⭐⭐⭐", value="3",
                         description="The support provided was neutral."),
    discord.SelectOption(label="⭐⭐", value="2",
                         description="The support provided was bad."),
    discord.SelectOption(label="⭐", value="1",
                         description="The support provided was the worst.")
]


class RatingView(discord.ui.View):
    def __init__(self, staff: discord.Member, user: discord.Member | discord.User, thread: discord.Thread = None):
        self.staff = staff
        self.user = user
        self.thread = thread
        super().__init__(timeout=180)

    async def on_timeout(self) -> None:
        self.disable_all_items()
        await self.message.edit(view=self)
        await self.message.reply(f"{emotes.bloxlink} Your feedback prompt timed out!")
        if self.thread:
            await self.thread.archive(locked=True)

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if not interaction.user.id == self.user.id:
            await interaction.response.send_message(content=f"{emotes.error} You can not use this.", ephemeral=True)
            return False
        return True

    @discord.ui.string_select(placeholder="Select a rating", options=RATE_OPTIONS)
    async def select_callback(self, select: discord.ui.Select, interaction: discord.Interaction):

        select.options = [discord.SelectOption(
            label=f"{'⭐' * int(select.values[0])}", default=True)]

        match select.values[0]:
            case "1":
                date = round(time.time())
                self.disable_all_items()
                await interaction.response.edit_message(view=self)

                await interaction.followup.send("Could you tell us why this option? Say 'Cancel' to cancel this prompt.")
                try:
                    message_in = await interaction.client.wait_for(
                        "message", check=lambda message: interaction.user.id == message.author.id and message.channel.id == interaction.channel.id, timeout=60.0)
                    message = message_in.content
                except asyncio.TimeoutError:
                    message = "None provided"
                    await interaction.followup.send("Your response prompt timed out.")

                if message_in.content.lower() == "cancel":
                    message = "None provided"
                    await interaction.followup.send("You cancelled this prompt.")

                await interaction.followup.send("Thank you for your feedback! You help us improve.")

                feedback = message
                await insert_one("rating", {"staff": self.staff.id, "user": self.user.id, "rating": 1, "date": date, "feedback": feedback})

                if self.thread:
                    await self.thread.archive(locked=True)
                self.stop()

            case "2":
                date = round(time.time())

                self.disable_all_items()

                await interaction.response.edit_message(view=self)

                await interaction.followup.send("Could you tell us why this option? Say 'Cancel' to cancel this prompt.")
                try:
                    message_in = await interaction.client.wait_for(
                        "message", check=lambda message: interaction.user.id == message.author.id and message.channel.id == interaction.channel.id, timeout=60.0)
                    message = message_in.content
                except asyncio.TimeoutError:
                    message = "None provided"
                    await interaction.followup.send("Your response prompt timed out.")

                if message_in.content.lower() == "cancel":
                    message = "None provided"
                    await interaction.followup.send("You cancelled this prompt.")

                await interaction.followup.send("Thank you for your feedback! You help us improve.")

                feedback = message
                await insert_one("rating", {"staff": self.staff.id, "user": self.user.id, "rating": 2, "date": date, "feedback": feedback})

                if self.thread:
                    await self.thread.archive(locked=True)
                self.stop()

            case "3":
                date = round(time.time())
                self.disable_all_items()

                await interaction.response.edit_message(view=self)

                await interaction.followup.send("Could you tell us why this option? Say 'Cancel' to cancel this prompt.")
                try:
                    message_in = await interaction.client.wait_for(
                        "message", check=lambda message: interaction.user.id == message.author.id and message.channel.id == interaction.channel.id, timeout=60.0)
                    message = message_in.content
                except asyncio.TimeoutError:
                    message = "None provided"
                    await interaction.followup.send("Your response prompt timed out.")

                if message_in.content.lower() == "cancel":
                    message = "None provided"
                    await interaction.followup.send("You cancelled this prompt.")

                await interaction.followup.send("Thank you for your feedback! You help us improve.")

                feedback = message
                await insert_one("rating", {"staff": self.staff.id, "user": self.user.id, "rating": 3, "date": date, "feedback": feedback})

                if self.thread:
                    await self.thread.archive(locked=True)
                self.stop()

            case "4":
                date = round(time.time())
                await insert_one("rating", {"staff": self.staff.id, "user": self.user.id, "rating": 4, "date": date})
                self.disable_all_items()

                await interaction.response.edit_message(view=self)
                await interaction.followup.send("Thank you so much for your rating!")

                if self.thread:
                    await self.thread.archive(locked=True)
                self.stop()

            case "5":
                date = round(time.time())
                await insert_one("rating", {"staff": self.staff.id, "user": self.user.id, "rating": 5, "date": date})

                self.disable_all_items()

                await interaction.response.edit_message(view=self)
                await interaction.followup.send("Thank you so much for your rating!")

                if self.thread:
                    await self.thread.archive(locked=True)
                self.stop()
