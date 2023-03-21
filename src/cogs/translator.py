import datetime

import discord
from config import colors, emotes
from discord.commands import Option, slash_command
from discord.ext import commands
import googletrans

from resources.CheckFailure import is_blacklisted

langs = ["af", "am", "ar", "az", "be", "bg", "bn", "bs", "ca", "ceb", "co", "cs", "cy", "da", "de", "el", "en", "eo", "es", "et", "eu", "fa", "fi", "fr", "fy", "ga", "gd", "gl", "gu", "ha", "haw", "he", "hi", "hmn", "hr", "ht", "hu", "hy", "id", "ig", "is", "it", "iw", "ja", "jw", "ka", "kk", "km", "kn", "ko", "ku", "ky", "la", "lb", "lo",
         "lt", "lv", "mg", "mi", "mk", "ml", "mn", "mr", "ms", "mt", "my", "ne", "nl", "no", "ny", "or", "pa", "pl", "ps", "pt", "ro", "ru", "rw", "sd", "si", "sk", "sl", "sm", "sn", "so", "sq", "sr", "st", "su", "sv", "sw", "ta", "te", "tg", "th", "tk", "tl", "tr", "tt", "ug", "uk", "ur", "uz", "vi", "xh", "yi", "yo", "zh", "zh-CN", "zh-TW", "zu"]


class Translator(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def get_langs(self, ctx: discord.AutocompleteContext):
        return [lang for lang in langs if lang.startswith(ctx.value.lower())]

    @commands.command(aliases=["tr"], name="translate")
    @commands.guild_only()
    @is_blacklisted()
    async def translate_text(self, ctx: commands.Context, target: str, *, query: str):

        if target.lower() not in langs:
            languages = ", ".join(langs)
            await ctx.reply(embed=discord.Embed(description=f"{emotes.error} Target language not found. Make sure it is one of these languages: ```{languages}```", color=colors.error))
            return

        translator = googletrans.Translator()

        translation = translator.translate(query, dest=target)
        translatedText = translation.text
        detectedSourceLanguage = translation.src
        pronounciation = translation.pronunciation

        embed = discord.Embed(timestamp=datetime.datetime.utcnow(
        ), color=colors.info, description=f"{emotes.bloxlink} Processing text from `{detectedSourceLanguage}` (detected) to `{target}`\n\n**Result:** \n`{translatedText}`")

        if pronounciation:
            embed.add_field(
                name="<:help:988166431109681214> Pronunciation", value=pronounciation)

        embed.set_footer(
            text=f"{ctx.author}", icon_url=ctx.author.display_avatar.url)

        await ctx.reply(embed=embed, mention_author=False)


def setup(bot):
    bot.add_cog(Translator(bot))
