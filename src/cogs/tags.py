import datetime
import time

import discord
from config import colors, emotes, links
from discord.commands import Option
from discord.ext import commands
from resources.CheckFailure import is_staff, is_blacklisted
from resources.modals import TagCreateModal, TagEditModal
from resources.mongoFunctions import get_aliases, get_tags, get_tags_and_alias, find_one, find_tag, update_tag, delete_one, return_all_tags
from resources.paginator import CustomPaginator


class Tags(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    tags = discord.SlashCommandGroup("tag", "Tag related commands.", guild_only=True)

    @tags.command(description="Create a new tag")
    @commands.guild_only()
    @is_staff()
    @is_blacklisted()
    async def create(self, ctx: discord.ApplicationContext):

        modal = TagCreateModal(self.bot, title="Create a new tag")
        await ctx.send_modal(modal)

    @tags.command(description="Delete an existent tag")
    @commands.guild_only()
    @is_staff()
    @is_blacklisted()
    async def delete(self, ctx: discord.ApplicationContext, name: Option(str, "The tag name you wish to remove", autocomplete=get_tags)):

        name = name.lower()
        find = await find_tag(name)

        if find:

            query = {"name": name}

            await delete_one("tags", query)
            success = emotes.success

            embed = discord.Embed(
                description=f"{success} Successfully **deleted**: {name}", color=colors.success)

            await ctx.respond(embed=embed)

        else:
            x = emotes.error
            embed = discord.Embed(
                description=f"{x} A tag with that name does not exist!", color=colors.error)
            await ctx.respond(embed=embed)

    @tags.command(description="Get information about a tag")
    @commands.guild_only()
    @is_blacklisted()
    async def info(self, ctx: discord.ApplicationContext, name: Option(str, "Search by name or alias", autocomplete=get_tags_and_alias)):

        name = name.lower()

        find = await find_tag(name)

        if find:

            name = find["name"]
            author = self.bot.get_user(find["author"])
            lastUpdateBy = self.bot.get_user(find["lastUpdateBy"])
            createdAt = find["createdAt"]
            lastUpdateAt = find["lastUpdateAt"]
            aliases = find["aliases"]
            aliases = ", ".join(aliases) if aliases != "None" else "None"
            content = find["content"]

            embed = discord.Embed(
                title=f":paperclips: Aliases: {aliases}", description=f":page_with_curl: Tag content:\n{content}", timestamp=datetime.datetime.utcnow(), color=colors.info)
            embed.set_author(
                icon_url=links.other, name=f"Tag information for: {name}")
            embed.add_field(name=":clipboard: Created By",
                            value=f"{author.mention} ({author.id})")
            embed.add_field(name=":safety_vest: Last Update By",
                            value=f"{lastUpdateBy.mention} ({lastUpdateBy.id})")
            embed.add_field(name=":calendar: Creation Date",
                            value=f"<t:{createdAt}:R>")
            embed.add_field(name=":timer: Last Update",
                            value=f"<t:{lastUpdateAt}:R>")
            embed.set_footer(icon_url=ctx.author.display_avatar.url,
                             text=f"{ctx.author.name}#{ctx.author.discriminator}")

            await ctx.respond(embed=embed)

        else:
            x = emotes.error
            embed = discord.Embed(
                description=f"{x} No tag found by this name", color=colors.error)
            await ctx.respond(embed=embed)

    @tags.command(description="Get the raw content of a tag")
    @commands.guild_only()
    @is_blacklisted()
    async def raw(self, ctx: discord.ApplicationContext, name: Option(str, "The tag name to get the raw content from", autocomplete=get_tags_and_alias)):

        name = name.lower()

        find = await find_tag(name)

        if find:

            content = find["content"]
            await ctx.respond(content=f":page_with_curl: Raw content for: {name}\n```\n{content}```", embed=None)

        else:
            x = emotes.error
            embed = discord.Embed(
                description=f"{x} No tag found by this name", color=colors.error)
            await ctx.respond(embed=embed)

    @tags.command(description="Edit an existent tag's content")
    @commands.guild_only()
    @is_staff()
    @is_blacklisted()
    async def edit(self, ctx: discord.ApplicationContext):
        await ctx.send_modal(TagEditModal(self.bot, title="Edit Tag"))

    @tags.command(description="Add or remove tag aliases")
    @commands.guild_only()
    @is_staff()
    @is_blacklisted()
    async def alias(self, ctx: discord.ApplicationContext, name: Option(str, "The tag name you wish to edit its alias", autocomplete=get_tags), choice: Option(str, "Add or remove an alias?", choices=["add", "remove"]), alias: Option(str, "New alias or alias to be removed", autocomplete=get_aliases)):

        await ctx.defer()

        name = name.lower()
        alias = alias.lower()
        check = {"name": name}

        find = await find_one("tags", check)
        updatedTime = round(time.time() * 1)

        if find:
            if choice == "add":
                oldAliases = find["aliases"]
                for al in oldAliases:
                    if al == alias:
                        aliasExists = True
                    else:
                        aliasExists = False

                newAliases = oldAliases

                if not aliasExists:

                    newAliases.append(alias)

                    if newAliases[0] == "None":
                        newAliases.remove("None")

                    aliases = {
                        "aliases": newAliases, "lastUpdateAt": updatedTime, "lastUpdateBy": ctx.author.id}

                    await update_tag(check, aliases)

                    success = emotes.success
                    embed = discord.Embed(
                        description=f"{success} **Added** alias: {alias}", color=colors.success)
                    await ctx.respond(embed=embed)

                else:
                    x = emotes.error
                    embed = discord.Embed(
                        description=f"{x} This alias already exists", color=colors.error)
                    await ctx.respond(embed=embed)

            elif choice == "remove":
                aliases = find["aliases"]

                try:
                    newAlias = aliases
                    newAlias.remove(alias)
                    if len(newAlias) == 0:
                        aliases.append("None")

                    update = {
                        "aliases": aliases, "lastUpdateAt": updatedTime, "lastUpdateBy": ctx.author.id}
                    await update_tag(check, update)

                    success = emotes.success
                    embed = discord.Embed(
                        description=f"{success} **Removed** alias: {alias}", color=colors.success, timestamp=datetime.datetime.utcnow())
                    await ctx.respond(embed=embed)

                except Exception:
                    x = emotes.error
                    embed = discord.Embed(
                        description=f"{x} No alias found for this tag", color=colors.error)
                    await ctx.respond(embed=embed)

            else:
                await ctx.respond("Invalid typeAlias selected.")
        else:
            x = emotes.error
            embed = discord.Embed(
                description=f"{x} No tag found by this name", color=colors.error)
            await ctx.respond(embed=embed)

    @tags.command(description="Get a tags list and a paginator")
    @commands.cooldown(1, 5, commands.BucketType.default)
    @commands.guild_only()
    @is_blacklisted()
    async def all(self, ctx: discord.ApplicationContext):

        await ctx.defer()

        pagPages = []
        tags = []

        tagsList = await return_all_tags()
        tagsList.sort(key=lambda x: x["name"])
        tags = [tag['name'] for tag in tagsList]

        tagsEmbed = discord.Embed(description=", ".join(
            tags), color=colors.info, timestamp=datetime.datetime.utcnow())
        emote = links.other
        tagsEmbed.set_author(icon_url=emote, name="Listing all tags:")
        tagsEmbed.set_footer(text="Use the paginator to go over the tags")
        pagPages.append(tagsEmbed)

        for findTag in tagsList:

            name = findTag["name"]
            aliases = ", ".join(findTag["aliases"])
            content = findTag["content"]
            author = await self.bot.get_or_fetch_user(findTag["author"])
            createdAt = findTag["createdAt"]
            lastUpdateAt = findTag["lastUpdateAt"]
            lastUpdateBy = await self.bot.get_or_fetch_user(findTag["lastUpdateBy"])

            embed = discord.Embed(
                title=f":paperclips: Aliases: {aliases}", description=f":page_with_curl: Tag content:\n{content}", timestamp=datetime.datetime.utcnow(), color=colors.info)
            embed.set_author(
                icon_url=emote, name=f"Tag information for: {name}")
            embed.add_field(name=":clipboard: Created By",
                            value=f"{author.mention} ({author.id})")
            embed.add_field(name=":safety_vest: Last Update By",
                            value=f"{lastUpdateBy.mention} ({lastUpdateBy.id})")
            embed.add_field(name=":calendar: Creation Date",
                            value=f"<t:{createdAt}:R>")
            embed.add_field(name=":timer: Last Update",
                            value=f"<t:{lastUpdateAt}:R>")
            embed.set_footer(icon_url=ctx.author.display_avatar.url,
                             text=f"{ctx.author.name}#{ctx.author.discriminator}")

            pagPages.append(embed)

        paginator = CustomPaginator(
            pages=pagPages, disable_on_timeout=True, timeout=60, show_disabled=False)
        await paginator.respond(ctx.interaction, ephemeral=False)

    @tags.command(description="Send a tag to the channel")
    @is_blacklisted()
    async def send(self, ctx: discord.ApplicationContext, name: Option(str, "The tag you want to display", autocomplete=get_tags_and_alias), text: Option(str, "Optional text before the tag (usually mentions)", required=False, default=None)):

        await ctx.defer()
        name = name.lower()

        find = await find_tag(name)

        if find:

            text = text if text is not None else ""
            tag = find["content"]

            await ctx.respond(f"{text} {tag}")

        else:
            x = emotes.error
            embed = discord.Embed(
                description=f"{x} No tag matching your search.", color=colors.error)
            await ctx.respond(embed=embed, delete_after=5.0)


def setup(bot):
    bot.add_cog(Tags(bot))
