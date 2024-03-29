import discord
from discord.ext import commands
from config import *


class CommandsContext(commands.Context):
    async def success(self, message: str, **kwargs):
        reply = kwargs.get("reply", True)
        mention_author = kwargs.get("mention_author", False)

        success_embed = discord.Embed(
            description=f"{emotes.success} {message}", color=colors.success)
        if reply or mention_author:
            await self.reply(embed=success_embed, mention_author=mention_author)
            return
        await self.send(embed=success_embed)

    async def error(self, message: str, **kwargs):
        reply = kwargs.get("reply", True)
        mention_author = kwargs.get("mention_author", False)

        error_embed = discord.Embed(
            description=f"{emotes.error} {message}", color=colors.error)
        if reply or mention_author:
            await self.reply(embed=error_embed, mention_author=mention_author)
            return
        await self.send(embed=error_embed)


class ApplicationCommandsContext(discord.ApplicationContext):
    async def success(self, message: str, **kwargs):
        ephemeral = kwargs.get("ephemeral", False)

        success_embed = discord.Embed(
            description=f"{emotes.success} {message}", color=colors.success)

        await self.respond(embed=success_embed, ephemeral=ephemeral)

    async def error(self, message: str, **kwargs):
        ephemeral = kwargs.get("ephemeral", False)

        error_embed = discord.Embed(
            description=f"{emotes.error} {message}", color=colors.error)

        await self.respond(embed=error_embed, ephemeral=ephemeral)
