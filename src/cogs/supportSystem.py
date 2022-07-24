from resources.CheckFailure import is_staff
from discord.commands import Option
from supportsystem.modal import FAQCreateModal, FAQEditModal
from supportsystem.view import FAQView, CloseThreadView, CreateThreadView
from config import COLORS
from discord.ext import commands
import discord


class SupportSystem(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot
        self.persistent_added = False

    @commands.Cog.listener()
    async def on_ready(self):
        if not self.persistent_added:
            self.bot.add_view(FAQView())
            self.bot.add_view(CloseThreadView())
            self.bot.add_view(CreateThreadView())
            self.persistent_added = True
            print("✅ Added support system views!")

    faq = discord.SlashCommandGroup("faq", "FAQs related commands.")

    @faq.command()
    @is_staff()
    async def create(self, ctx, category: Option(str, "The category the FAQ will be created in", choices=["verification", "api", "binds", "premium", "other"])):
        """Create a FAQ."""
        modal = FAQCreateModal(category)
        await ctx.send_modal(modal)

    @faq.command()
    @is_staff()
    async def edit(self, ctx, category: Option(str, "The category the FAQ will be edited in", choices=["verification", "api", "binds", "premium", "other"])):
        """Edit a FAQ."""
        modal = FAQEditModal(category)
        await ctx.send_modal(modal)

    @discord.slash_command()
    @commands.is_owner()
    async def send_faq(self, ctx, channel: discord.TextChannel):
        """Owner only command to send the FAQs to a channel."""

        embed = discord.Embed(color=COLORS["info"], title=":wave: Welcome to Bloxlink's FAQ!",
                              description="Welcome! You have come to the right place if you are looking for help with Bloxlink.\n\n<:lifesaver:986648046592983150> **How do I use this FAQ system?**\n\nSelect the category from the dropdown you think your question fits in, a new message will pop up with questions related to the category selected. Found your question? Click the respective button number to get your answer.")

        await channel.send(embed=embed, view=FAQView())
        await ctx.respond("Done")

    @discord.slash_command()
    @commands.is_owner()
    async def update_faq(self, ctx: discord.ApplicationContext, channel: discord.TextChannel, message: str):
        """Owner only command to update the support system message."""

        message = await channel.fetch_message(int(message))
        embed = discord.Embed(color=COLORS["info"], title=":wave: Welcome to Bloxlink's support system!",
                              description="Hello! You have come to the right place if you are looking for help with Bloxlink.\n\n<:lifesaver:986648046592983150> **How do I use the FAQ system?**\n\nClick the **Open FAQ** button to open the FAQs. Select the category you think your question fits in. Found your question? Click the respective button number!")

        await message.edit(embed=embed, view=FAQView())
        await ctx.respond("Done")

    @discord.slash_command()
    @commands.is_owner()
    async def send_get_support(self, ctx: discord.ApplicationContext, channel: discord.TextChannel):
        """Owner only command to send the get support message."""
        embed = discord.Embed(color=COLORS["info"], title=":wave: Welcome to Bloxlink's premium support system!",
                              description="Thanks for purchasing premium! You know have access to priority support, our team is ready to asssist you in just a few minutes.\n\n<:lifesaver:986648046592983150> **How do I open a thread?**\n\nClick the **Get Support** button, a thread will get privately created for you to get on instant contact with our staff team.")
        await channel.send(embed=embed, view=CreateThreadView())
        await ctx.respond("Done")


def setup(bot):
    bot.add_cog(SupportSystem(bot))
