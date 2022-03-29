import discord
from discord.ext import commands
from discord.commands import slash_command, Option
import requests
import json
from config import LINKS, EMOTES, COLORS


langs = ["af", "am", "ar", "az", "be", "bg", "bn", "bs", "ca", "ceb", "co", "cs", "cy", "da", "de", "el", "en", "eo", "es", "et", "eu", "fa", "fi", "fr", "fy", "ga", "gd", "gl", "gu", "ha", "haw", "he", "hi", "hmn", "hr", "ht", "hu", "hy", "id", "ig", "is", "it", "iw", "ja", "jw", "ka", "kk", "km", "kn", "ko", "ku", "ky", "la", "lb", "lo", "lt", "lv", "mg", "mi", "mk", "ml", "mn", "mr", "ms", "mt", "my", "ne", "nl", "no", "ny", "or", "pa", "pl", "ps", "pt", "ro", "ru", "rw", "sd", "si", "sk", "sl", "sm", "sn", "so", "sq", "sr", "st", "su", "sv", "sw", "ta", "te", "tg", "th", "tk", "tl", "tr", "tt", "ug", "uk", "ur", "uz", "vi", "xh", "yi", "yo", "zh", "zh-CN", "zh-TW", "zu"]

class Translator(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def get_langs(self, ctx: discord.AutocompleteContext):
        return [lang for lang in langs if lang.startswith(ctx.value.lower())]

    @slash_command(description="Translate text to a language")
    async def translate(self, ctx: discord.ApplicationContext, target: Option(str, "Language you want the text get translated to", autocomplete=get_langs), *, query: Option(str, "Text you want to translate")):

        url = "https://google-translate1.p.rapidapi.com/language/translate/v2"

        payload = f"q={query}&target={target}"
        headers = {
            'content-type': "application/x-www-form-urlencoded",
            'accept-encoding': "application/gzip",
            'x-rapidapi-key': "1cbb863212msh4b966b8001850eap1f4df0jsnbec81431720e",
            'x-rapidapi-host': "google-translate1.p.rapidapi.com"
            }

        response = requests.request("POST", url, data=payload, headers=headers)
        status = response.status_code
        response = json.loads(response.text)
        
        if status == 200:
            
            translatedText = response["data"]["translations"][0]["translatedText"]
            translatedText.replace("&#39", "'")
            detectedSourceLanguage = response["data"]["translations"][0]["detectedSourceLanguage"]

            infoEmote = EMOTES["info"]
            embed = discord.Embed(timestamp=discord.utils.utcnow,color=COLORS["info"],description=f"{infoEmote} Processing text from `{detectedSourceLanguage}`(detected) to `{target}`\n\n**Result:** \n`{translatedText}`")
            embed.set_footer(text=f"Requested by: {ctx.author}", icon_url=ctx.author.display_avatar.url)
            await ctx.respond(embed=embed)

        elif status == 400:
            message = response["error"]["message"]
            x = EMOTES["error"]
            embed = discord.Embed(description=f"{x} {message}", color=COLORS["error"])

            await ctx.respond(embed=embed)

        elif "quota" in response["message"]:
            x = EMOTES["error"]
            embed = discord.Embed(description=f"{x} Exhausted motnhly quota", color=COLORS["error"])
            await ctx.respond(embed=embed)

        else:
            x = EMOTES["error"]
            embed = discord.Embed(description=f"{x} Something went wrong:\n```py\n{response}```", color=COLORS["error"])
            await ctx.respond(embed=embed)

def setup(bot):
    bot.add_cog(Translator(bot))