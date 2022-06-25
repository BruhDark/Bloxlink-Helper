import asyncio
from datetime import datetime
import discord
from discord import SelectOption
from discord.ui import View, button, Button
from discord import ButtonStyle
from Resources.mongoFunctions import delete_one, find_one, return_all, insert_one
from config import COLORS, LINKS

class ThreadButton(discord.ui.Button):
    def __init__(self, topic: str):
        super().__init__(style=ButtonStyle.blurple, label="Get Support", emoji="<:lifesaver:986648046592983150>")
        self.topic = topic

    async def callback(self, interaction: discord.Interaction):

        await interaction.response.defer()

        userThread = await find_one("support-users", {"user": interaction.user.id})
        
        if userThread is not None:
            thread = interaction.channel.get_thread(userThread["thread"])
            await interaction.followup.send(f"<:BloxlinkDead:823633973967716363> You are already in a support thread. Please use head to {thread.mention} to join the thread.", ephemeral=True)
            return

        thread = await interaction.channel.create_thread(name=f"{interaction.user.name} - {self.topic}", reason="Support Thread", type=discord.ChannelType.private_thread)

        embedT = discord.Embed(color=COLORS["info"], timestamp=datetime.utcnow(), title="Support Thread")
        embedT.add_field(name="<:user:988229844301131776> Created By", value=interaction.user.mention)
        embedT.add_field(name="<:help:988166431109681214> Topic", value=self.topic)
        embedT.add_field(name="<:thread:988229846188564500> Thread", value=thread.mention)
        
        Lchannel = discord.utils.get(interaction.guild.channels, name="support-threads")
        log = await Lchannel.send(embed=embedT)
        
        object = await insert_one("support-users", {"user": interaction.user.id, "thread": thread.id, "log": log.id})

        embed = discord.Embed(color=COLORS["info"], timestamp=datetime.utcnow(), title="Support Thread", description=f":wave: Welcome to your support thread!\n\n<:BloxlinkSilly:823634273604468787> Our Helpers will assist you in a few minutes. While you wait, please provide as much detail as possible! Consider providing screenshots or/and anything that helps the team to solve your issue faster.\n\n<:time:987836664355373096> Our team is taking too long? If 10 minutes have passed, you can click the **Ping Helpers** button, this will notify our team you are here!")
        embed.set_author(name=f"{interaction.user.name}#{interaction.user.discriminator} | ID: {object.inserted_id}", icon_url=interaction.user.display_avatar.url)
        embed.set_footer(text=f"To close this thread, press the padlock below. Only Helpers can close this thread")
        
        ThreadView = CloseThreadView(thread)
        message = await thread.send(content=interaction.user.mention, embed=embed, view=ThreadView)
        ThreadView.message = message
        await ThreadView.enableButton()

        await interaction.followup.send(f"<:BloxlinkSilly:823634273604468787> You have created a support thread. Please use head to {thread.mention} to join the thread.", ephemeral=True)

class NumberButton(discord.ui.Button):
    def __init__(self, label, embed):
        super().__init__(style=ButtonStyle.grey, label=label)
        self.embed = embed

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.send_message(embed=self.embed, ephemeral=True)

async def format_buttons(questions: list):
    """Formats the buttons for the support system"""
    view = View(timeout=None)

    for index, question in enumerate(questions):

        q = question["q"]
        embed = discord.Embed(color=COLORS["info"], title=f"<:BloxlinkConfused:823633690910916619> {q}", description=question["a"])

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

class CloseThreadView(View):
    def __init__(self, thread: int):
        super().__init__(timeout=None)
        self.thread: discord.Thread = thread

    async def enableButton(self) -> None:
        await asyncio.sleep(float(60*10))

        self.children[1].disabled = False
        await self.message.edit(view=self)

    @discord.ui.button(style=ButtonStyle.red, label="​", emoji="<:padlock:987837727741464666>")
    async def ct_callback(self, button: discord.Button, interaction: discord.Interaction):

        if not interaction.user.guild_permissions.manage_threads:
            await interaction.response.send_message("<:BloxlinkDead:823633973967716363> You do not have permission to close this thread.")
            return
        
        button.disabled = True
        
        object = await find_one("support-users", {"thread": self.thread.id})
        user = object["user"]
        topic = self.thread.name.split(" - ")[1]

        await delete_one("support-users", {"thread": self.thread.id})
        await interaction.response.edit_message(view=self)
        await interaction.followup.send("<:padlock:987837727741464666> This thread has been marked as closed.")

        await self.thread.archive(locked=True)

        embedT = discord.Embed(color=COLORS["error"], timestamp=datetime.utcnow(), title="Support Thread Closed")
        embedT.add_field(name="<:user:988229844301131776> Created By", value=f"<@{user}>")
        embedT.add_field(name="<:help:988166431109681214> Topic", value=topic)
        embedT.add_field(name="<:thread:988229846188564500> Thread", value=self.thread.mention)
        embedT.add_field(name="<:user:988229844301131776> Closed By", value=f"{interaction.user.mention} ({interaction.user.id})")

        Lchannel = discord.utils.get(interaction.guild.channels, name="support-threads")
        
        message = interaction.client.get_message(object["log"])
        message = await Lchannel.fetch_message(object["log"]) if message is None else message

        await message.edit(embed=embedT)

    @discord.ui.button(style=ButtonStyle.green, emoji="<:notification:990034677836427295>", label="Ping Helpers", disabled=True)
    async def callback(self, button: Button, interaction: discord.Interaction):

        Hrole = interaction.guild.get_role(412791520316358656)
        THrole = interaction.guild.get_role(818919735193632858)

        await interaction.channel.send(f"<:notification:990034677836427295> {Hrole.mention} {THrole.mention}", allowed_mentions=discord.AllowedMentions(roles=True))
        button.disabled = True
        await interaction.response.edit_message(view=self)

class FAQView(View):
    def __init__(self):
        super().__init__(timeout=None)

    options = [
        SelectOption(label="Verification", value="verification", emoji="<:link:986648044525199390>", description="Link/Remove a Roblox account, nickname templates"),
        SelectOption(label="Binding", value="binds", emoji="<:box:987447660510334976>", description="Add/Remove group/role/badge binds"),
        SelectOption(label="Bloxlink API", value="api", emoji="<:api:987447659025547284>", description="How to use the API, how to get an API key"),
        SelectOption(label="Premium/Pro", value="premium", emoji="<:thunderbolt:987447657104560229>", description="How to get Premium/Pro, what are the perks, how to activate a server"),
        SelectOption(label="Other", value="other", emoji="<:confused:987447655384875018>", description="None of the above categories match your question?"),
    ]

    @discord.ui.select(placeholder="Select a category", min_values=1, max_values=1, options=options)
    async def select_callback(self, select: discord.ui.Select, interaction: discord.Interaction):

        await interaction.response.defer()
        
        if select.values[0] == "verification":
            questions = await return_all("faq-verification")

            qs = []
            for qsn, question in enumerate(questions):

                q = question["q"]
                qs.append(f"**Q{str(qsn + 1)}** - {q}")

            embed = discord.Embed(color=COLORS["info"], title="Verification Related Questions", description="\n".join(qs))
            embed.set_footer(text="Did not find an answer? Click the Get Support button to create a support thread.", icon_url=LINKS["other"])
            view = await format_buttons(questions)
            view.add_item(ThreadButton("Verification"))
            await interaction.followup.send(embed=embed, view=view, ephemeral=True)

        elif select.values[0] == "binds":
            questions = await return_all("faq-binds")

            qs = []
            for qsn, question in enumerate(questions):

                q = question["q"]
                qs.append(f"**Q{str(qsn + 1)}** - {q}")

            embed = discord.Embed(color=COLORS["info"], title="Binds Related Questions", description="\n".join(qs))
            embed.set_footer(text="Did not find an asnwer? Click the Get Support button to create a support thread.", icon_url=LINKS["other"])

            view = await format_buttons(questions)
            view.add_item(ThreadButton("Binds"))
            await interaction.followup.send(embed=embed, view=view, ephemeral=True)

        elif select.values[0] == "api":
            questions = await return_all("faq-api")

            qs = []
            for qsn, question in enumerate(questions):

                q = question["q"]
                qs.append(f"**Q{str(qsn + 1)}** - {q}")

            embed = discord.Embed(color=COLORS["info"], title="Bloxlink API Related Questions", description="\n".join(qs))
            embed.set_footer(text="Did not find an asnwer? Click the Get Support button to create a support thread.", icon_url=LINKS["other"])

            view = await format_buttons(questions)
            view.add_item(ThreadButton("API"))
            await interaction.followup.send(embed=embed, view=view, ephemeral=True)

        elif select.values[0] == "premium":
            questions = await return_all("faq-premium")

            qs = []
            for qsn, question in enumerate(questions):

                q = question["q"]
                qs.append(f"**Q{str(qsn + 1)}** - {q}")

            embed = discord.Embed(color=COLORS["info"], title="Premium Related Questions", description="\n".join(qs))
            embed.set_footer(text="Did not find an asnwer? Click the Get Support button to create a support thread.", icon_url=LINKS["other"])

            view = await format_buttons(questions)
            view.add_item(ThreadButton("Premium"))
            await interaction.followup.send(embed=embed, view=view, ephemeral=True)

        elif select.values[0] == "other":
            questions = await return_all("faq-other")

            qs = []
            for qsn, question in enumerate(questions):

                q = question["q"]
                qs.append(f"**Q{str(qsn + 1)}** - {q}")

            embed = discord.Embed(color=COLORS["info"], title="Other Non-Categorised Questions", description="\n".join(qs))
            embed.set_footer(text="Did not find an asnwer? Click the Get Support button to create a support thread.", icon_url=LINKS["other"])

            view = await format_buttons(questions)
            view.add_item(ThreadButton("Other"))
            await interaction.followup.send(embed=embed, view=view, ephemeral=True)


class SupportView(View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(Button(style=ButtonStyle.url, emoji="<:book:986647611740147712>", label="Bloxlink Documentation", url="https://docs.blox.link/"))
        self.add_item(Button(style=ButtonStyle.url, emoji="<:link:986648044525199390>", label="Verify with Bloxlink", url="https://blox.link/verify"))
        
    
    @button(custom_id="getHelpButton", style=ButtonStyle.blurple, emoji="<:help:988166431109681214>", label="Open FAQ")
    async def callback(self, button: button, interaction: discord.Interaction):

        embed = discord.Embed(title=":wave: Welcome to Bloxlink's FAQ!", description="\n<:BloxlinkConfused:823633690910916619> **How does this work?**\nSelect the category, from the dropdown, that you think your question matches. You will get prompted with some questions, they all have a number. Click the respective number on the buttons below them and get an answer!\n\n<:BloxlinkNervous:823633774939865120> **Did not find an answer?**\nClick the **Get Support** button to create a support thread. Our team will be glad to assist you!", color=COLORS["info"])

        await interaction.response.send_message(embed=embed, view=FAQView(), ephemeral=True)
