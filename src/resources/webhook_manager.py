import discord
from discord.ext import commands
import aiohttp
import os
import traceback
from datetime import datetime

from config import emotes, colors


async def send_command_error(ctx: commands.Context | discord.ApplicationContext, error: Exception):
    async with aiohttp.ClientSession() as session:
        url = os.getenv("WEBHOOK_URL")
        webhook = discord.Webhook.from_url(url, session=session)
        tb = ''.join(traceback.format_exception(
            error, error, error.__traceback__))
        tb = tb + "\n"

        embed = discord.Embed(
            title=f"{emotes.error} Something went wrong", color=colors.error, timestamp=datetime.utcnow())
        embed.description = f"```py\n{tb}```"

        embed.add_field(name="Author", value=f"{ctx.author} ({ctx.author.id})")
        embed.add_field(
            name="Command", value=f"{ctx.command.qualified_name}")
        embed.add_field(
            name="Guild", value=f"{ctx.guild.name} ({ctx.guild.id})")

        await webhook.send(embed=embed)


async def send_error(error: Exception):
    async with aiohttp.ClientSession() as session:
        url = os.getenv("WEBHOOK_URL")
        webhook = discord.Webhook.from_url(url, session=session)

        tb = ''.join(traceback.format_exception(
            error, error, error.__traceback__))
        tb = tb + "\n"

        embed = discord.Embed(
            title=f"{emotes.error} Failed to post FAQ message", color=colors.error, timestamp=datetime.utcnow())
        embed.description = f"```py\n{tb}```"

        await webhook.send(embed=embed)
