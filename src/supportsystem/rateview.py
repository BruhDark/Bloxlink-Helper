import asyncio
import discord
from discord import ButtonStyle
import time
from resources.mongoFunctions import insert_one

RATE_OPTIONS = [
    discord.SelectOption(label="⭐⭐⭐⭐⭐", value="5",
                         description="The support provided was the best."),
    discord.SelectOption(label="⭐⭐⭐⭐", value="4",
                         description="The support provided was good."),
    discord.SelectOption(label="⭐⭐⭐", value="3",
                         description="The support provided was a bit good."),
    discord.SelectOption(label="⭐⭐", value="2",
                         description="The support provided was bad."),
    discord.SelectOption(label="⭐", value="1",
                         description="The support provided was the worst.")
]


class RatingView(discord.ui.View):
    def __init__(self, staff: discord.Member, thread: discord.Thread = None):
        self.staff = staff
        self.thread = thread
        super().__init__()

    async def on_timeout(self) -> None:
        self.disable_all_items()
        await self.message.edit(view=self)
        await self.message.reply("Your feedback prompt timed out!")

    @discord.ui.string_select(placeholder="Select a rating", options=RATE_OPTIONS)
    async def select_callback(self, select: discord.ui.Select, interaction: discord.Interaction):
        if select.values[0] == "1":
            date = round(time.time())
            self.disable_all_items()
            await interaction.response.edit_message(view=self)

            await interaction.followup.send("Could you tell us why this option? Say 'Cancel' to cancel this prompt.")
            try:
                message = await interaction.client.wait_for(
                    "message", check=lambda message: interaction.user.id == message.author.id and message.guild is None, timeout=60.0)
            except asyncio.TimeoutError:
                message = "None provided"
                await interaction.followup.send("Your prompt timed out.")

            if message.content.lower() == "cancel":
                message = "None provided"
                await interaction.followup.send("You cancelled this prompt.")

            await interaction.followup.send("Thank you for your feedback! You help us improve.")

            feedback = message.content
            await insert_one("rating", {"user": self.staff.id, "rating": 1, "date": date, "feedback": feedback})

            if self.thread:
                await self.thread.archive(locked=True)
            self.stop()

        elif select.values[0] == "2":
            date = round(time.time())

            self.disable_all_items()

            await interaction.response.edit_message(view=self)

            await interaction.followup.send("Could you tell us why this option? Say 'Cancel' to cancel this prompt.")
            try:
                message = await interaction.client.wait_for(
                    "message", check=lambda message: interaction.user.id == message.author.id and message.guild is None, timeout=60.0)
            except asyncio.TimeoutError:
                message = "None provided"
                await interaction.followup.send("Your prompt timed out.")

            if message.content.lower() == "cancel":
                message = "None provided"
                await interaction.followup.send("You cancelled this prompt.")

            await interaction.followup.send("Thank you for your feedback! You help us improve.")

            feedback = message.content
            await insert_one("rating", {"user": self.staff.id, "rating": 2, "date": date, "feedback": feedback})

            if self.thread:
                await self.thread.archive(locked=True)
            self.stop()

        elif select.values[0] == "3":
            date = round(time.time())
            self.disable_all_items()

            await interaction.response.edit_message(view=self)

            await interaction.followup.send("Could you tell us why this option? Say 'Cancel' to cancel this prompt.")
            try:
                message = await interaction.client.wait_for(
                    "message", check=lambda message: interaction.user.id == message.author.id and message.guild is None, timeout=60.0)
            except asyncio.TimeoutError:
                message = "None provided"
                await interaction.followup.send("Your prompt timed out.")

            if message.content.lower() == "cancel":
                message = "None provided"
                await interaction.followup.send("You cancelled this prompt.")

            await interaction.followup.send("Thank you for your feedback! You help us improve.")

            feedback = message.content
            await insert_one("rating", {"user": self.staff.id, "rating": 3, "date": date, "feedback": feedback})

            if self.thread:
                await self.thread.archive(locked=True)
            self.stop()

        elif select.values[0] == "4":
            date = round(time.time())
            await insert_one("rating", {"user": self.staff.id, "rating": 4, "date": date})
            self.disable_all_items()

            await interaction.response.edit_message(view=self)
            await interaction.followup.send("Thank you so much for your rating!")

            if self.thread:
                await self.thread.archive(locked=True)
            self.stop()

        elif select.values[0] == "5":
            date = round(time.time())
            await insert_one("rating", {"user": self.staff.id, "rating": 5, "date": date})

            self.disable_all_items()

            await interaction.response.edit_message(view=self)
            await interaction.followup.send("Thank you so much for your rating!")

            if self.thread:
                await self.thread.archive(locked=True)
            self.stop()

        else:
            interaction.response.send_message(content="Something went wrong.")
