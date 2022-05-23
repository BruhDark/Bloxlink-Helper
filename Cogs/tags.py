import datetime
import time

import discord
from config import COLORS, EMOTES, LINKS
from discord.commands import Option
from discord.ext import commands, pages
from Resources.CheckFailure import is_staff, is_blacklisted
from Resources.modals import TagCreateModal, TagEditModal
from Resources.mongoFunctions import get_aliases, get_tags, get_tags_and_alias, find_one, find_tag, update_tag, delete_one, return_all_tags


class Tags(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    tags = discord.SlashCommandGroup("tag", "Tag related commands.")

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
        check = {"name": name}

        find = await find_one(check)

        if find:

            query = {"name": name}
            oldContent = find["content"]
            createdBy = find["author"]
            id = find["_id"]

            await delete_one(query)
            success = EMOTES["success"]

            embed = discord.Embed(
                description=f"{success} Successfully **deleted**: {name}", color=COLORS["success"])

            await ctx.respond(embed=embed)

        else:
            x = EMOTES["error"]
            embed = discord.Embed(
                description=f"{x} A tag with that name does not exist!", color=COLORS["error"])
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
                title=f":paperclips: Aliases: {aliases}", description=f":page_with_curl: Tag content:\n{content}", timestamp=datetime.datetime.utcnow(), color=COLORS["info"])
            embed.set_author(
                icon_url=LINKS["other"], name=f"Tag information for: {name}")
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
            x = EMOTES["error"]
            embed = discord.Embed(
                description=f"{x} No tag found by this name", color=COLORS["error"])
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
            x = EMOTES["error"]
            embed = discord.Embed(
                description=f"{x} No tag found by this name", color=COLORS["error"])
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

        find = await find_one(check)
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

                    success = EMOTES["success"]
                    embed = discord.Embed(
                        description=f"{success} **Added** alias: {alias}", color=COLORS["success"], timestamp=datetime.datetime.utcnow())
                    await ctx.respond(embed=embed)

                else:
                    x = EMOTES["error"]
                    embed = discord.Embed(
                        description=f"{x} This alias already exists", color=COLORS["error"])
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

                    success = EMOTES["success"]
                    embed = discord.Embed(
                        description=f"{success} **Removed** alias: {alias}", color=COLORS["success"], timestamp=datetime.datetime.utcnow())
                    await ctx.respond(embed=embed)

                except Exception:
                    x = EMOTES["error"]
                    embed = discord.Embed(
                        description=f"{x} No alias found for this tag", color=COLORS["error"])
                    await ctx.respond(embed=embed)

            else:
                await ctx.respond("Invalid typeAlias selected.")
        else:
            x = EMOTES["error"]
            embed = discord.Embed(
                description=f"{x} No tag found by this name", color=COLORS["error"])
            await ctx.respond(embed=embed)

    @tags.command(description="Get a tags list and a paginator")
    @commands.cooldown(1, 5, commands.BucketType.default)
    @commands.guild_only()
    @is_staff()
    @is_blacklisted()
    async def all(self, ctx: discord.ApplicationContext):

        await ctx.defer()

        pagPages = []
        tags = []

        tagsList  = await return_all_tags()
        for tag in tagsList:
            tags.append(tag["name"])

        tags.sort()

        tagsEmbed = discord.Embed(description=", ".join(
            tags), color=COLORS["info"], timestamp=datetime.datetime.utcnow())
        emote = LINKS["other"]
        tagsEmbed.set_author(icon_url=emote, name="Listing all tags:")
        tagsEmbed.set_footer(text="Use the paginator to go over the tags")
        pagPages.append(tagsEmbed)

        for findTag in tags:

            check = {"name": findTag}
            find = await find_one(check)

            name = find["name"]
            aliases = ", ".join(find["aliases"])
            content = find["content"]
            author = await self.bot.get_or_fetch_user(find["author"])
            createdAt = find["createdAt"]
            lastUpdateAt = find["lastUpdateAt"]
            lastUpdateBy = await self.bot.get_or_fetch_user(find["lastUpdateBy"])

            embed = discord.Embed(
                title=f":paperclips: Aliases: {aliases}", description=f":page_with_curl: Tag content:\n{content}", timestamp=datetime.datetime.utcnow(), color=COLORS["info"])
            embed.set_author(
                icon_url=LINKS["success"], name=f"Tag information for: {name}")
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

        paginator = pages.Paginator(
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
            x = EMOTES["error"]
            embed = discord.Embed(
                description=f"{x} No tag matching your search.", color=COLORS["error"])
            await ctx.respond(embed=embed, delete_after=5.0)


def setup(bot):
    bot.add_cog(Tags(bot))
