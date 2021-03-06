import datetime
import json

import discord
import aiohttp
from config import COLORS, EMOTES, LINKS
from discord.commands import Option, slash_command
from discord.ext import commands

langs = ["af", "am", "ar", "az", "be", "bg", "bn", "bs", "ca", "ceb", "co", "cs", "cy", "da", "de", "el", "en", "eo", "es", "et", "eu", "fa", "fi", "fr", "fy", "ga", "gd", "gl", "gu", "ha", "haw", "he", "hi", "hmn", "hr", "ht", "hu", "hy", "id", "ig", "is", "it", "iw", "ja", "jw", "ka", "kk", "km", "kn", "ko", "ku", "ky", "la", "lb", "lo",
         "lt", "lv", "mg", "mi", "mk", "ml", "mn", "mr", "ms", "mt", "my", "ne", "nl", "no", "ny", "or", "pa", "pl", "ps", "pt", "ro", "ru", "rw", "sd", "si", "sk", "sl", "sm", "sn", "so", "sq", "sr", "st", "su", "sv", "sw", "ta", "te", "tg", "th", "tk", "tl", "tr", "tt", "ug", "uk", "ur", "uz", "vi", "xh", "yi", "yo", "zh", "zh-CN", "zh-TW", "zu"]


class Translator(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def get_langs(self, ctx: discord.AutocompleteContext):
        return [lang for lang in langs if lang.startswith(ctx.value.lower())]

    @commands.command(aliases=["tr"])
    @commands.guild_only()
    async def translate(self, ctx: commands.Context, target: str, *, query: str):

        if target.lower() not in langs:
            languages = ", ".join(langs)
            await ctx.reply(embed=discord.Embed(description=f"{EMOTES['error']} Target language not found. Make sure it is one of these languages: ```{languages}```", color=COLORS["error"]))
            return

        url = "https://google-translate1.p.rapidapi.com/language/translate/v2"

        payload = f"q={query}&target={target}"
        headers = {
            'content-type': "application/x-www-form-urlencoded",
            'accept-encoding': "application/gzip",
            'x-rapidapi-key': "1cbb863212msh4b966b8001850eap1f4df0jsnbec81431720e",
            'x-rapidapi-host': "google-translate1.p.rapidapi.com"
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(url, data=payload, headers=headers) as response:
                data = await response.json()

        try:
          error = data["error"]["code"]
        except KeyError:
            error = None
        
        if error is None:

            translatedText = data["data"]["translations"][0]["translatedText"]
            translatedText.encode(encoding="utf-8")
            detectedSourceLanguage = data["data"]["translations"][0]["detectedSourceLanguage"]

            infoEmote = EMOTES["info"]
            embed = discord.Embed(timestamp=datetime.datetime.utcnow(
            ), color=COLORS["info"], description=f"{infoEmote} Processing text from `{detectedSourceLanguage}` (detected) to `{target}`\n\n**Result:** \n`{translatedText}`")
            embed.set_footer(
                text=f"Requested by: {ctx.author}", icon_url=ctx.author.display_avatar.url)
            await ctx.reply(embed=embed, mention_author=False)

        elif error == 400:
            message = data["error"]["message"]
            x = EMOTES["error"]
            embed = discord.Embed(
                description=f"{x} {message}", color=COLORS["error"])

            await ctx.send(embed=embed)

        elif "quota" in data["error"]["message"]:
            x = EMOTES["error"]
            embed = discord.Embed(
                description=f"{x} Exhausted motnhly quota", color=COLORS["error"])
            await ctx.send(embed=embed)

        else:
            x = EMOTES["error"]
            embed = discord.Embed(
                description=f"{x} Something went wrong:\n```py\n{data}```", color=COLORS["error"])
            await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Translator(bot))
