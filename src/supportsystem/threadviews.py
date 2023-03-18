import discord
from discord import ButtonStyle
from discord import Button
from resources.mongoFunctions import insert_one, find_one, delete_one
from config import colors, links, emotes
import datetime
import asyncio
from supportsystem.rateview import RatingView
from resources.CheckFailure import is_staff
from discord import SelectOption


class CloseThreadView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    async def enableButton(self) -> None:
        if self.children[0].disabled == True:
            return

        await asyncio.sleep(float(60*10))

        if self.children[0].disabled == True:
            return

        self.children[1].disabled = False
        await self.message.edit(view=self)

    @discord.ui.button(style=ButtonStyle.red, label="​", emoji="<:padlock:987837727741464666>", custom_id="CloseThreadButton")
    async def ct_callback(self, button: discord.Button, interaction: discord.Interaction):

        # if not interaction.user.guild_permissions.manage_threads:
        #   await interaction.response.send_message("<:BloxlinkDead:823633973967716363> You do not have permission to close this thread.", ephemeral=True)
        #   return

        button.disabled = True
        self.children[1].disabled = True
        thread: discord.Thread = interaction.channel

        object = await find_one("support-users", {"thread": thread.id})
        user = object["user"]

        await delete_one("support-users", {"thread": thread.id})
        await interaction.response.edit_message(view=self)
        await interaction.followup.send(f"<:padlock:987837727741464666> This support thread has been marked as solved by {interaction.user.mention}")

        Lchannel = discord.utils.get(
            interaction.guild.channels, name="support-threads")

        message = interaction.client.get_message(object["log"])
        message = await Lchannel.fetch_message(object["log"]) if message is None else message

        staff_role = discord.utils.get(
            interaction.guild.roles, name="Staff"
        )

        if staff_role in interaction.user.roles:
            rateView = RatingView(interaction.user)

            user = await interaction.client.get_or_fetch_user(user)

            rateEmbed = discord.Embed(title="<:BloxlinkHappy:823633735446167552> Thanks for contacting us!",
                                      description="We appreciate you and want to know your satisfaction level of the support provided by our team.\nFeel free to rate us by clicking the :star: (star) and telling us your satisfaction level. Being the first one, 1 (I was not satisfied by the support given), and the last one 5 (I was very satified by the support given).", color=colors.info)
            rateEmbed.timestamp = datetime.datetime.utcnow()
            rateEmbed.set_author(
                name=f"Hello, {user.name}!", icon_url=user.display_avatar.url)
            rateEmbed.set_footer(
                text="Thank you for choosing Bloxlink! We hope you have a great day!", icon_url=links.other)

            try:
                await user.send(embed=rateEmbed, view=rateView)
                await thread.archive(locked=True)
            except:
                await interaction.channel.send(content=f"{user.mention} I was unable to DM you.", embed=rateEmbed, view=RatingView(interaction.user, thread))

        else:
            history = interaction.channel.history()
            async for message in history:
                if staff_role in message.author.roles:
                    staff = message.author
                    break

            user = await interaction.client.get_or_fetch_user(user)

            rateEmbed = discord.Embed(title="<:BloxlinkHappy:823633735446167552> Thank you for contacting us!",
                                      description="We appreciate you and want to know your satisfaction level of the support provided by our team.\nFeel free to rate us by clicking the :star: (star) and telling us your satisfaction level. Being the first one, 1 (I was not satisfied by the support given), and the last one 5 (I was very satified by the support given).", color=colors.info)
            rateEmbed.timestamp = datetime.datetime.utcnow()
            rateEmbed.set_author(
                name=f"Hello, {user.name}!", icon_url=user.display_avatar.url)
            rateEmbed.set_footer(
                text="Thank you for choosing Bloxlink! We hope you have a great day!", icon_url=links.other)

            try:
                await user.send(embed=rateEmbed, view=RatingView(staff))
                await thread.archive(locked=True)
            except:
                await interaction.channel.send(content=f"{user.mention} I was unable to DM you.", embed=rateEmbed, view=RatingView(staff, thread))

        await message.delete()

    @discord.ui.button(style=ButtonStyle.green, emoji="<:notification:990034677836427295>", label="Ping Helpers", disabled=True, custom_id="PingHelpersButton")
    async def callback(self, button: Button, interaction: discord.Interaction):
        user = await find_one("support-users", {"thread": interaction.channel.id})
        if interaction.user.id != user["user"]:
            await interaction.response.send_message("<:BloxlinkDead:823633973967716363> You are not the thread author!", ephemeral=True)
            return

        Hrole = interaction.guild.get_role(412791520316358656)
        THrole = interaction.guild.get_role(818919735193632858)
        button.disabled = True

        await interaction.response.edit_message(view=self)
        await interaction.channel.send(f"<:notification:990034677836427295> {Hrole.mention} {THrole.mention}", allowed_mentions=discord.AllowedMentions(roles=True))

        await self.enableButton()


class ThreadButton(discord.ui.Button):
    def __init__(self, topic: str, disabled: bool = False):
        super().__init__(style=ButtonStyle.green, label="Yes, it is correct",
                         emoji=emotes.bloxlink, disabled=disabled)
        self.topic = topic

    async def callback(self, interaction: discord.Interaction):

        await interaction.response.defer(ephemeral=True)

        supportBannedRole = discord.utils.get(
            interaction.guild.roles, name="support banned")
        if supportBannedRole in interaction.user.roles:
            await interaction.response.send_message(
                "<:BloxlinkDead:823633973967716363> You are support banned. Contact our staff team for more information.", ephemeral=True)
            return

        userThread = await find_one("support-users", {"user": interaction.user.id})

        if userThread is not None:
            thread = interaction.channel.get_thread(userThread["thread"])
            await interaction.followup.send(f"<:BloxlinkDead:823633973967716363> You are already in a support thread. Please head to {thread.mention} to join the thread.", ephemeral=True)
            return

        try:
            thread = await interaction.channel.create_thread(name=f"{interaction.user.name} - {self.topic}", reason="Support Thread", type=discord.ChannelType.private_thread)
        except:
            thread = await interaction.channel.create_thread(name=f"{interaction.user.name} - {self.topic}", reason="Support Thread", type=discord.ChannelType.public_thread)

        await interaction.followup.send(f"<:BloxlinkSilly:823634273604468787> You have created a support thread. Please head to {thread.mention} to join the thread.", ephemeral=True)

        embedT = discord.Embed(
            color=colors.info, timestamp=datetime.datetime.utcnow(), title="Support Thread")
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

        embed = discord.Embed(color=colors.info, timestamp=datetime.datetime.utcnow(), title="Support Thread",
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


class CreateThreadView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.string_select(placeholder="Select a motive", custom_id="ThreadMotiveSelect", options=[SelectOption(label="Verification", value="verification", emoji="<:link:986648044525199390>"),
                                                                                                      SelectOption(
                                                                                                          label="Binds", value="binds", emoji="<:box:987447660510334976>"),
                                                                                                      SelectOption(
                                                                                                          label="Bloxlink API", value="api", emoji="<:api:987447659025547284>"),
                                                                                                      SelectOption(
                                                                                                          label="Premium/Pro", value="premium", emoji="<:thunderbolt:987447657104560229>"),
                                                                                                      SelectOption(label="Other", value="other", emoji="<:confused:987447655384875018>")])
    async def select_callback(self,  select: discord.ui.Select, interaction: discord.Interaction):
        view = discord.ui.View()
        view.add_item(ThreadButton(select.values[0].capitalize()))
        await interaction.response.send_message(content=f"`{select.values[0].capitalize()}` is your motive for this new thread. Is this correct? If not, please select the correct thread motive.", view=view, ephemeral=True)
