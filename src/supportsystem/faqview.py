import asyncio
from datetime import datetime
import time

import discord
from config import COLORS, LINKS
from discord import ButtonStyle, SelectOption
from discord.ui import Button, View, button
from resources.mongoFunctions import return_all


class NumberButton(discord.ui.Button):
    def __init__(self, label, embed):
        super().__init__(style=ButtonStyle.blurple, label=label)
        self.embed = embed

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.send_message(embed=self.embed, ephemeral=True)


async def format_buttons(questions: list):
    """Formats the buttons for the support system"""
    view = View(timeout=None)

    for index, question in enumerate(questions):

        q = question["q"]
        embed = discord.Embed(
            color=COLORS["info"], title=f"<:BloxlinkConfused:823633690910916619> {q}", description=question["a"])

        try:
            image = question["image"]
            if image is None:
                raise Exception("No image")
            embed.set_image(url=image)
        except Exception:
            pass

        Button = NumberButton(str(index + 1), embed)

        view.add_item(Button)

    return view


class FAQView(View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(Button(style=ButtonStyle.url, emoji="<:book:986647611740147712>",
                      label="Tutorials", url="https://blox.link/tutorials"))
        self.add_item(Button(style=ButtonStyle.url, emoji="<:link:986648044525199390>",
                      label="Verify with Bloxlink", url="https://blox.link/verify"))

    options = [
        SelectOption(label="Verification", value="verification", emoji="<:link:986648044525199390>",
                     description="Link/Remove a Roblox account, nickname templates"),
        SelectOption(label="Binds", value="binds", emoji="<:box:987447660510334976>",
                     description="Add/Remove group/role/badge binds"),
        SelectOption(label="Bloxlink API", value="api", emoji="<:api:987447659025547284>",
                     description="How to use the API, how to get an API key"),
        SelectOption(label="Premium/Pro", value="premium", emoji="<:thunderbolt:987447657104560229>",
                     description="How to get Premium/Pro, what are the perks, how to activate a server"),
        SelectOption(label="Other", value="other", emoji="<:confused:987447655384875018>",
                     description="None of the above categories match your question?"),
    ]

    @discord.ui.select(placeholder="Select a category", min_values=1, max_values=1, options=options, custom_id="FAQSelect")
    async def select_callback(self, select: discord.ui.Select, interaction: discord.Interaction):

        await interaction.response.defer()

        embed = discord.Embed(color=COLORS["info"])
        embed.set_footer(
            text="Did not find an answer? Use our support channels.", icon_url=LINKS["other"])
        view = None

        if select.values[0] == "verification":
            questions = await return_all("faq-verification")

            qs = [f"**Q{str(qsn + 1)}** - {question['q']}" for qsn,
                  question in enumerate(questions)]

            embed.title = "Verification Related Questions"
            embed.description = "\n".join(qs)

            view = await format_buttons(questions)

        elif select.values[0] == "binds":
            questions = await return_all("faq-binds")

            qs = [f"**Q{str(qsn + 1)}** - {question['q']}" for qsn,
                  question in enumerate(questions)]

            embed.title = "Binds Related Questions"
            embed.description = "\n".join(qs)

            view = await format_buttons(questions)

        elif select.values[0] == "api":
            questions = await return_all("faq-api")

            qs = [f"**Q{str(qsn + 1)}** - {question['q']}" for qsn,
                  question in enumerate(questions)]

            embed.title = "API Related Questions"
            embed.description = "\n".join(qs)

            view = await format_buttons(questions)

        elif select.values[0] == "premium":
            questions = await return_all("faq-premium")

            qs = [f"**Q{str(qsn + 1)}** - {question['q']}" for qsn,
                  question in enumerate(questions)]

            embed.title = "Premium Related Questions"
            embed.description = "\n".join(qs)

            view = await format_buttons(questions)

        elif select.values[0] == "other":
            questions = await return_all("faq-other")

            qs = [f"**Q{str(qsn + 1)}** - {question['q']}" for qsn,
                  question in enumerate(questions)]

            embed.title = "Other Non-Categorised Questions"
            embed.description = "\n".join(qs)

            view = await format_buttons(questions)

        await interaction.followup.send(embed=embed, view=view, ephemeral=True)


class SupportView(View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(Button(style=ButtonStyle.url, emoji="<:book:986647611740147712>",
                      label="Tutorials", url="https://blox.link/tutorials"))
        self.add_item(Button(style=ButtonStyle.url, emoji="<:link:986648044525199390>",
                      label="Verify with Bloxlink", url="https://blox.link/verify"))

    @button(custom_id="getHelpButton", style=ButtonStyle.blurple, emoji="<:help:988166431109681214>", label="Open FAQ")
    async def callback(self, button: button, interaction: discord.Interaction):

        embed = discord.Embed(title=":wave: Welcome to Bloxlink's FAQ!",
                              description="\n<:BloxlinkConfused:823633690910916619> **How does this work?**\nSelect the category, from the dropdown, that you think your question matches. You will get prompted with some questions, they all have a number. Click the respective number on the buttons below them and get an answer!\n\n<:BloxlinkNervous:823633774939865120> **Did not find an answer?**\nState your issue with as much detail as possible in our support channels, our team will be glad to assit you!", color=COLORS["info"])

        await interaction.response.send_message(embed=embed, view=FAQView(), ephemeral=True)
