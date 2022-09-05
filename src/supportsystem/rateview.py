import asyncio
import discord
from discord import ButtonStyle
import time
from resources.mongoFunctions import insert_one


class RatingView(discord.ui.View):
    def __init__(self):
        super().__init__()

    async def on_timeout(self) -> None:
        self.disable_all_items()
        await self.message.edit(view=self)
        await self.message.reply("Your feedback prompt timed out!")

    @discord.ui.button(style=ButtonStyle.gray, label=" ", emoji="⭐", custom_id="1star")
    async def one_star(self, button: discord.Button, interaction: discord.Interaction):
        date = round(time.time())

        button.style = ButtonStyle.blurple
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
        await insert_one("rating", {"user": interaction.user.id, "rating": 1, "date": date, "feedback": feedback})

        self.stop()

    @discord.ui.button(style=ButtonStyle.gray, label=" ", emoji="⭐", custom_id="2stars")
    async def two_stars(self, button: discord.Button, interaction: discord.Interaction):
        date = round(time.time())

        for children in self.children:
            if children.custom_id == "3stars":
                break
            children.style = ButtonStyle.blurple

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
        await insert_one("rating", {"user": interaction.user.id, "rating": 2, "date": date, "feedback": feedback})

        self.stop()

    @discord.ui.button(style=ButtonStyle.gray, label=" ", emoji="⭐", custom_id="3stars")
    async def three_stars(self, button: discord.Button, interaction: discord.Interaction):
        date = round(time.time())

        for children in self.children:
            if children.custom_id == "4stars":
                break
            children.style = ButtonStyle.blurple
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
        await insert_one("rating", {"user": interaction.user.id, "rating": 3, "date": date, "feedback": feedback})

        self.stop()

    @discord.ui.button(style=ButtonStyle.gray, label=" ", emoji="⭐", custom_id="4stars")
    async def four_stars(self, button: discord.Button, interaction: discord.Interaction):
        date = round(time.time())
        await insert_one("rating", {"user": interaction.user.id, "rating": 4, "date": date})

        for children in self.children:
            if children.custom_id == "5stars":
                break
            children.style = ButtonStyle.blurple
        self.disable_all_items()

        await interaction.response.edit_message(view=self)
        await interaction.followup.send("Thank you so much for your rating!")
        self.stop()

    @discord.ui.button(style=ButtonStyle.gray, label=" ", emoji="⭐", custom_id="5stars")
    async def five_stars(self, button: discord.Button, interaction: discord.Interaction):
        date = round(time.time())
        await insert_one("rating", {"user": interaction.user.id, "rating": 5, "date": date})

        for children in self.children:
            children.style = ButtonStyle.blurple
        self.disable_all_items()

        await interaction.response.edit_message(view=self)
        await interaction.followup.send("Thank you so much for your rating!")
        self.stop()
