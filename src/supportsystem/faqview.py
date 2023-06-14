from datetime import datetime

import discord
from config import colors, links
from discord import ButtonStyle, SelectOption
from discord.ui import Button, View, button
from resources.mongoFunctions import return_all
from resources.mongoFunctions import find_one, insert_one
from supportsystem.threadviews import CloseThreadView


class ThreadButtonFAQ(discord.ui.Button):
    def __init__(self, topic: str):
        super().__init__(style=ButtonStyle.blurple, label="Get Support",
                         emoji="<:lifesaver:986648046592983150>", custom_id="PersistentThreadButton")
        self.topic = topic

    async def callback(self, interaction: discord.Interaction):

        await interaction.response.defer(ephemeral=True)

        supportBannedRole = discord.utils.get(
            interaction.guild.roles, name="support banned")
        if supportBannedRole in interaction.user.roles:
            await interaction.response.send_message(
                "<:BloxlinkDead:823633973967716363> You are support banned.", ephemeral=True)
            return

        userThread = await find_one("support-users", {"user": interaction.user.id})

        if userThread is not None:
            thread = interaction.channel.get_thread(userThread["thread"])
            await interaction.followup.send(f"<:BloxlinkDead:823633973967716363> You are already in a support thread. Please head to {thread.mention} to join the thread.", ephemeral=True)
            return

        channel = interaction.guild.get_channel(1017439501452324864)

        try:
            thread = await channel.create_thread(name=f"{interaction.user.name} - {self.topic}", reason="Support Thread", type=discord.ChannelType.private_thread)
        except:
            thread = await channel.create_thread(name=f"{interaction.user.name} - {self.topic}", reason="Support Thread", type=discord.ChannelType.public_thread)

        await interaction.followup.send(f"<:BloxlinkSilly:823634273604468787> You have created a support thread. Please head to {thread.mention} to join the thread.", ephemeral=True)

        embedT = discord.Embed(
            color=colors.info, timestamp=datetime.utcnow(), title="Support Thread")
        embedT.add_field(
            name="<:user:988229844301131776> Created By", value=interaction.user.mention)
        embedT.add_field(
            name="<:help:988166431109681214> Topic", value=self.topic)
        embedT.add_field(
            name="<:thread:988229846188564500> Thread", value=thread.mention)

        Lchannel = discord.utils.get(
            interaction.guild.channels, name="support-threads")
        log = await Lchannel.send(embed=embedT)

        object = await insert_one("support-users", {"user": interaction.user.id, "thread": thread.id, "log": log.id})

        embed = discord.Embed(color=colors.info, timestamp=datetime.utcnow(), title="Support Thread",
                              description=f":wave: Welcome to your support thread!\n\n<:BloxlinkSilly:823634273604468787> Our Helpers will assist you in a few minutes. While you wait, please provide as much detail as possible! Consider providing screenshots or/and anything that helps the team to solve your issue faster.\n\n<:time:987836664355373096> Our team is taking too long? If 10 minutes have passed, you can click the **Ping Helpers** button, this will notify our team you are here!")
        embed.set_author(name=f"{interaction.user.name}#{interaction.user.discriminator} | ID: {object.inserted_id}",
                         icon_url=interaction.user.display_avatar.url)
        embed.set_footer(
            text=f"To close this thread, press the padlock below.")

        ThreadView = CloseThreadView()
        message = await thread.send(content=interaction.user.mention, embed=embed, view=ThreadView)
        ThreadView.message = message
        await message.pin(reason="Support Thread Message")
        await ThreadView.enableButton()


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
            color=colors.info, title=f"<:BloxlinkConfused:823633690910916619> {q}", description=question["a"])

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

        embed = discord.Embed(color=colors.info)
        embed.set_footer(
            text="Did not find an answer? Use our support channel.", icon_url=links.other)
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

        premiumRole = discord.utils.get(
            interaction.guild.roles, id=372175493040177152)

        if premiumRole in interaction.user.roles:
            view.add_item(ThreadButtonFAQ(select.values[0].capitalize()))

        await interaction.followup.send(embed=embed, view=view, ephemeral=True)


class SupportView(View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(Button(style=ButtonStyle.url, emoji="<:book:986647611740147712>",
                      label="Tutorial", url="https://www.youtube.com/watch?v=SbDltmom1R8&list=PLz7SOP-guESEI9EnEV-1ftn6SzcqQumRc&index=4"))
        self.add_item(Button(style=ButtonStyle.url, emoji="<:link:986648044525199390>",
                      label="Verify with Bloxlink", url="https://blox.link/verify"))

    @button(custom_id="getHelpButton", style=ButtonStyle.blurple, emoji="<:help:988166431109681214>", label="Open FAQ")
    async def callback(self, button: button, interaction: discord.Interaction):

        embed = discord.Embed(title=":wave: Welcome to Bloxlink's FAQ!",
                              description="\n<:BloxlinkConfused:823633690910916619> **How does this work?**\nSelect the category, from the dropdown, that you think your question matches. You will get prompted with some questions, they all have a number. Click the respective number on the buttons below them and get an answer!\n\n<:BloxlinkNervous:823633774939865120> **Did not find an answer?**\nState your issue with as much detail as possible in our support channels, our team will be glad to assit you!", color=colors.info)

        await interaction.response.send_message(embed=embed, view=FAQView(), ephemeral=True)
