import discord
from discord import ButtonStyle
import time
from resources.mongoFunctions import insert_one


class RatingView(discord.ui.View):
    def __init__(self):
        super().__init__()

    async def on_timeout(self) -> None:
        self.disable_all_items()
        embed = self.message.embeds[0]
        field = embed.fields[0]
        field.name = "You took too long to select a rating!"
        await self.message.edit(view=self, embed=embed)

    @discord.ui.button(style=ButtonStyle.gray, label=" ", emoji="⭐", custom_id="1star")
    async def one_star(self, button: discord.Button, interaction: discord.Interaction):
        date = round(time.time())
        await insert_one("rating", {"user": interaction.user.id, "rating": 1, "date": date})

        button.style = ButtonStyle.blurple
        self.disable_all_items()

        rateEmbed = self.message.embeds[0]
        field = rateEmbed.fields[0]
        field.name = "Thank you so much for your rating!"

        await interaction.response.edit_message(embed=rateEmbed, view=self)

    @discord.ui.button(style=ButtonStyle.gray, label=" ", emoji="⭐", custom_id="2stars")
    async def two_stars(self, button: discord.Button, interaction: discord.Interaction):
        date = round(time.time())
        await insert_one("rating", {"user": interaction.user.id, "rating": 2, "date": date})

        for children in self.children:
            if children.custom_id == "3stars":
                break
            children.style = ButtonStyle.blurple

        self.disable_all_items()

        rateEmbed = self.message.embeds[0]
        field = rateEmbed.fields[0]
        field.name = "Thank you so much for your rating!"
        await interaction.response.edit_message(embed=rateEmbed, view=self)

    @discord.ui.button(style=ButtonStyle.gray, label=" ", emoji="⭐", custom_id="3stars")
    async def three_stars(self, button: discord.Button, interaction: discord.Interaction):
        date = round(time.time())
        await insert_one("rating", {"user": interaction.user.id, "rating": 3, "date": date})

        for children in self.children:
            if children.custom_id == "4stars":
                break
            children.style = ButtonStyle.blurple
        self.disable_all_items()

        rateEmbed = self.message.embeds[0]
        field = rateEmbed.fields[0]
        field.name = "Thank you so much for your rating!"

        await interaction.response.edit_message(embed=rateEmbed, view=self)

    @discord.ui.button(style=ButtonStyle.gray, label=" ", emoji="⭐", custom_id="4stars")
    async def four_stars(self, button: discord.Button, interaction: discord.Interaction):
        date = round(time.time())
        await insert_one("rating", {"user": interaction.user.id, "rating": 4, "date": date})

        for children in self.children:
            if children.custom_id == "5stars":
                break
            children.style = ButtonStyle.blurple
        self.disable_all_items()

        rateEmbed = self.message.embeds[0]
        field = rateEmbed.fields[0]
        field.name = "Thank you so much for your rating!"

        await interaction.response.edit_message(embed=rateEmbed, view=self)

    @discord.ui.button(style=ButtonStyle.gray, label=" ", emoji="⭐", custom_id="5stars")
    async def five_stars(self, button: discord.Button, interaction: discord.Interaction):
        date = round(time.time())
        await insert_one("rating", {"user": interaction.user.id, "rating": 5, "date": date})

        for children in self.children:
            children.style = ButtonStyle.blurple
        self.disable_all_items()

        rateEmbed = self.message.embeds[0]
        field = rateEmbed.fields[0]
        field.name = "Thank you so much for your rating!"

        await interaction.response.edit_message(embed=rateEmbed, view=self)
