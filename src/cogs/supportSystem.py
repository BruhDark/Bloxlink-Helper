from resources.CheckFailure import is_staff
from discord.commands import Option
from resources.context import ApplicationCommandsContext
from resources.mongoFunctions import delete_one, return_all
from supportsystem.modal import FAQCreateModal, FAQEditModal
from supportsystem.faqview import FAQView
from supportsystem.threadviews import CloseThreadView, CreateThreadView
from config import colors, emotes, badges
from discord.ext import commands
import discord


class SupportSystem(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot
        self.persistent_added = False

    faq = discord.SlashCommandGroup("faq", "FAQs related commands.")

    @commands.Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.bot.add_view(FAQView())
            self.bot.add_view(CreateThreadView())
            self.bot.add_view(CloseThreadView())
            print("✅ Loaded support system views.")

    @faq.command()
    @is_staff()
    async def create(self, ctx: discord.ApplicationContext, category: Option(str, "The category the FAQ will be created in", choices=["verification", "api", "binds", "premium", "other"])):
        """Create a FAQ question"""
        modal = FAQCreateModal(category)
        await ctx.send_modal(modal)

    @faq.command()
    @is_staff()
    async def edit(self, ctx, category: Option(str, "The category the FAQ will be edited in", choices=["verification", "api", "binds", "premium", "other"])):
        """Edit a FAQ question"""
        modal = FAQEditModal(category)
        await ctx.send_modal(modal)

    @faq.command()
    @is_staff()
    async def delete(self, ctx: ApplicationCommandsContext, category: Option(str, "The category the FAQ is in", choices=["verification", "api", "binds", "premium", "other"]), faq_id: Option(str, "The FAQ number in the category")):
        """Delete a FAQ question"""

        faqs = await return_all(f"faq-{category}")
        faqs = [{"index": f"{faqn+1}", "question": f"{faq['q']}"}
                for faqn, faq in enumerate(faqs)]

        get_faq = [faq['question']
                   for faq in faqs if faq['index'] == faq_id][0]
        check = {
            "q": get_faq}

        await delete_one(f"faq-{category}", check)
        await ctx.success(f"Successfully deleted FAQ #**{faq_id}** from **{category}** category")

    @discord.slash_command()
    @commands.is_owner()
    async def send_faq(self, ctx, channel: discord.TextChannel):
        """Owner only command to send the FAQs to a channel."""

        embed = discord.Embed(color=colors.info, title=f"{emotes.info} Frequently Asked Questions",
                              description=f"Welcome to our Frequently Asked Questions channel. This channel contains useful information for commonly asked questions. If you don't find the answer to your question, feel free to use the <#372181186816245770> channel.")

        embed.add_field(inline=False, name=f"{emotes.box} Resources",
                        value="[Invite Bloxlink](https://blox.link/invite)\n[Dashboard](https://blox.link/dashboard)\n[Commands](https://blox.link/commands)\n[Pricing](https://blox.link/pricing)\n[Work with us](https://blox.link/jobs)\n[Developer Portal](https://blox.link/dashboard/developer)\n")

        embed.add_field(inline=False, name=f"{emotes.question} How do I see the Frequently Asked Questions?",
                        value="Select the category that best fits your question from the dropdown menu. Once you've selected a category, a new message will appear with questions related to the category you selected. If you find your question, click the corresponding button number to get your answer.")

        await channel.send(embed=embed, view=FAQView())
        await ctx.respond("Done")

    @discord.slash_command()
    @commands.is_owner()
    async def send_get_support(self, ctx: discord.ApplicationContext, channel: discord.TextChannel):
        """Owner only command to send the get support message."""
        embed = discord.Embed(color=colors.info, title=f"{emotes.success} Thank you for supporting us!",
                              description="We appreciate your support towards us! You can now access our priority support system, which opens a private thread with our staff team. This way, you can get a faster and more knowledgeable response.")

        embed.add_field(name=f"{emotes.question} How do I open a thread?",
                        value="Select the reason for your thread from the select menu. This will help our staff team to answer your query faster. Once you have chosen the correct thread reason, confirm it, and your private thread will be opened.")
        await channel.send(embed=embed, view=CreateThreadView())
        await ctx.respond("Done")


def setup(bot):
    bot.add_cog(SupportSystem(bot))
