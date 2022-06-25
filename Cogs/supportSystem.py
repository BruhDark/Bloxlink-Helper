import discord
from discord.ext import commands
from config import COLORS
from SupportSystem.view import SupportView, CloseThreadView
from SupportSystem.modal import FAQCreateModal, FAQEditModal
from discord.commands import Option
from Resources.CheckFailure import is_staff

class SupportSystem(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        self.bot.add_view(SupportView())
        self.bot.add_view(CloseThreadView())

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


    @faq.command()
    @is_staff()
    @commands.is_owner()
    async def send(self, ctx, channel: discord.TextChannel):

        embed = discord.Embed(color=COLORS["info"], title=":wave: Welcome to Bloxlink's support system!", description="Welcome! You have come to the right place if you are looking for help with Bloxlink.\n\n<:lifesaver:986648046592983150> **How to use the support system**\n\nIt is very easy to use our support system! You can navigate through a quick Frequently Asked Questions menu and get a fast answer by clicking the **Open FAQ** button. If your question is not in any of the categories, you can always open a support thread by clicking the **Get Support** button below the FAQs. Easy, isn't it?")

        await channel.send(embed=embed, view=SupportView())
        await ctx.respond("Done")

    @faq.command()
    @is_staff()
    @commands.is_owner()
    async def update(self, ctx: discord.ApplicationContext, channel: discord.TextChannel, message: str):

        message = await channel.fetch_message(int(message))
        embed = discord.Embed(color=COLORS["info"], title=":wave: Welcome to Bloxlink's support system!", description="Hello! You have come to the right place if you are looking for help with Bloxlink.\n\n<:lifesaver:986648046592983150> **How to use the support system**\n\nIt is very easy to use our support system! You can navigate through a quick Frequently Asked Questions menu and get a fast answer by clicking the **Open FAQ** button. If your question is not in any of the categories, you can always open a support thread by clicking the **Get Support** button below the FAQs. Easy, isn't it?")

        await message.edit(embed=embed, view=SupportView())
        await ctx.respond("Done")

def setup(bot):
    bot.add_cog(SupportSystem(bot))