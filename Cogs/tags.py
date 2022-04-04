import asyncio
import datetime
import time

import discord
import pymongo
from config import COLORS, EMOTES, LINKS
from discord.commands import Option, permissions, slash_command
from discord.ext import commands, pages


class Tags(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.database = self.bot.database

    tags = discord.SlashCommandGroup("tag", "Tag related commands.")

    async def is_staff(self, ctx: discord.ApplicationContext):

        role = discord.utils.get(ctx.guild.roles, name="Helpers")
        permission = ctx.author.guild_permissions.manage_messages

        check = True if role in ctx.author.roles else False

        return True if check or permission else False

    async def get_tags(self, ctx: discord.ApplicationContext):

        collection = self.bot.database["tags"]
        tags = []
        for tag in collection.find():
            tags.append(tag["name"])

        return [tag for tag in tags if tag.startswith(ctx.value.lower())]

    async def get_tags_and_alias(self, ctx: discord.ApplicationContext):

        collection = self.bot.database["tags"]
        tags = []

        for tag in collection.find():
            tags.append(tag["name"])
            if tag["aliases"] != ["None"]:
                tags.extend(tag["aliases"])

        return [tag for tag in tags if tag.startswith(ctx.value.lower())]

    async def get_aliases(self, ctx: discord.ApplicationContext):

        collection = self.bot.database["tags"]
        aliases = []

        for tag in collection.find():
            if tag["aliases"] != ["None"]:
                aliases.extend(tag["aliases"])

        return [alias for alias in aliases if alias.startswith(ctx.value.lower())]

    @tags.command(description="Create a new tag")
    async def create(self, ctx: discord.ApplicationContext, name: Option(str, "The new tag name"), content: Option(str, "The tag content"), aliases: Option(str, "Aliases for this tag, separated by a comma, no space", required=False, default=None)):

        if await Tags.is_staff(self, ctx):
            collection = self.bot.database["tags"]
            createdAt = round(time.time() * 1)
            name = name.lower()
            aliases = aliases.lower() if aliases is not None else aliases
            aliases = aliases.replace(
                " ", "") if aliases is not None else aliases
            aliases = aliases.split(",") if aliases is not None else ["None"]
            content = content.replace("\\n", "\n")

            loading = EMOTES["loading"]
            embed = discord.Embed(
                description=f"{loading} Working on it....", color=COLORS["info"])

            await ctx.respond(embed=embed)
            message = await ctx.interaction.original_message()

            newTag = {"name": name, "aliases": aliases, "content": content, "author": ctx.author.id,
                      "lastUpdateBy": ctx.author.id, "createdAt": createdAt, "lastUpdateAt": createdAt}
            check = {"name": name}
            check2 = {"aliases": aliases}
            find2 = collection.find_one(
                check2) if aliases[0] != "None" else False

            if collection.find_one(check) or find2:
                error = EMOTES["error"]
                embed = discord.Embed(
                    description=f"{error} A tag with that name/alias already exists!", color=COLORS["error"])
                await message.edit(embed=embed)

            else:
                item = collection.insert_one(newTag)
                aliases = ", ".join(aliases)

                embed = discord.Embed(
                    title=f":paperclips: Aliases: {aliases}", description=f":page_with_curl: Tag content:\n{content}", color=COLORS["success"], timestamp=datetime.datetime.utcnow())
                embed.set_footer(
                    icon_url=LINKS["other"], text=f"Item ID: {item.inserted_id}")
                embed.set_author(
                    icon_url=LINKS["success"], name=f"Successfully created tag: {name}")

                await message.edit(embed=embed)

        else:
            x = EMOTES["error"]
            embed = discord.Embed(
                description=f"{x} You do not have permission to run this command.", color=COLORS["error"])
            await ctx.respond(embed=embed, ephemeral=True)

    @tags.command(description="Delete an existent tag")
    async def delete(self, ctx: discord.ApplicationContext, name: Option(str, "The tag name you wish to remove", autocomplete=get_tags)):

        if await Tags.is_staff(self, ctx):
            collection = self.bot.database["tags"]
            name = name.lower()
            check = {"name": name}

            loading = EMOTES["loading"]
            embed = discord.Embed(
                description=f"{loading} Working on it....", color=COLORS["info"])
            await ctx.respond(embed=embed)
            message = await ctx.interaction.original_message()

            find = collection.find_one(check)

            if find:

                query = {"name": name}
                oldContent = find["content"]
                createdBy = find["author"]
                id = find["_id"]

                collection.delete_one(query)
                success = EMOTES["success"]

                embed = discord.Embed(
                    description=f"{success} Successfully **deleted**: {name}", color=COLORS["success"])

                await message.edit(embed=embed)

            else:
                x = EMOTES["error"]
                embed = discord.Embed(
                    description=f"{x} A tag with that name does not exist!", color=COLORS["error"])
                await message.edit(embed=embed)

        else:
            x = EMOTES["error"]
            embed = discord.Embed(
                description=f"{x} You do not have permission to run this command.", color=COLORS["error"])
            await ctx.respond(embed=embed, ephemeral=True)

    @tags.command(description="Get information about a tag")
    async def info(self, ctx: discord.ApplicationContext, name: Option(str, "Search by name or alias", autocomplete=get_tags_and_alias)):

        collection = self.bot.database["tags"]
        name = name.lower()
        check = {"name": name}
        check2 = {"aliases": name}

        loading = EMOTES["loading"]
        embed = discord.Embed(
            description=f"{loading} Working on it....", color=COLORS["info"])
        await ctx.respond(embed=embed)
        message = await ctx.interaction.original_message()

        find = collection.find_one(check)
        if not find:
            find = collection.find_one(check2)

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

            await message.edit(embed=embed)

        else:
            x = EMOTES["error"]
            embed = discord.Embed(
                description=f"{x} No tag found by this name", color=COLORS["error"])
            await message.edit(embed=embed)

    @tags.command(description="Get the raw content of a tag")
    async def raw(self, ctx: discord.ApplicationContext, name: Option(str, "The tag name to get the raw content from", autocomplete=get_tags_and_alias)):

        if await Tags.is_staff(self, ctx):
            collection = self.bot.database["tags"]
            name = name.lower()

            loading = EMOTES["loading"]
            embed = discord.Embed(
                description=f"{loading} Working on it....", color=COLORS["info"])
            await ctx.respond(embed=embed)
            message = await ctx.interaction.original_message()
            check = {"name": name}
            check2 = {"aliases": name}

            find = collection.find_one(check)
            if not find:
                find = collection.find_one(check2)

            if find:

                content = find["content"]
                await message.edit(content=f":page_with_curl: Raw content for: {name}\n```\n{content}```", embed=None)

            else:
                x = EMOTES["error"]
                embed = discord.Embed(
                    description=f"{x} No tag found by this name", color=COLORS["error"])
                await message.edit(embed=embed)

        else:
            x = EMOTES["error"]
            embed = discord.Embed(
                description=f"{x} You do not have permission to run this command.", color=COLORS["error"])
            await ctx.respond(embed=embed, ephemeral=True)

    @tags.command(description="Edit an existent tag's content")
    async def edit(self, ctx: discord.ApplicationContext, name: Option(str, "The tag name you want to edit", autocomplete=get_tags), content: Option(str, "The new content for this tag")):

        if await Tags.is_staff(self, ctx):
            loading = EMOTES["loading"]
            embed = discord.Embed(
                description=f"{loading} Working on it....", color=COLORS["info"])
            await ctx.respond(embed=embed)
            message = await ctx.interaction.original_message()

            collection = self.bot.database["tags"]
            name = name.lower()
            check = {"name": name}

            content = content.replace("\\n", "\n")
            find = collection.find_one(check)

            if find:

                oldContent = find["content"]

                updatedTime = round(time.time() * 1)
                update = {"$set": {
                    "content": content, "lastUpdateAt": updatedTime, "lastUpdateBy": ctx.author.id}}
                collection.update_one(check, update)

                embed = discord.Embed(
                    description=f":page_with_curl: New tag content:\n{content}", color=COLORS["success"], timestamp=datetime.datetime.utcnow())
                embed.set_author(
                    icon_url=LINKS["success"], name=f"Done! Successfully edited: {name}")
                await message.edit(embed=embed)

            else:
                x = EMOTES["error"]
                embed = discord.Embed(
                    description=f"{x} No tag found by this name", color=COLORS["error"])
                await message.edit(embed=embed)
        else:
            x = EMOTES["error"]
            embed = discord.Embed(
                description=f"{x} You do not have permission to run this command.", color=COLORS["error"])
            await ctx.respond(embed=embed, ephemeral=True)

    @tags.command(description="Add or remove tag aliases")
    async def alias(self, ctx: discord.ApplicationContext, name: Option(str, "The tag name you wish to edit its alias", autocomplete=get_tags), choice: Option(str, "Add or remove an alias?", choices=["add", "remove"]), alias: Option(str, "New alias or alias to be removed", autocomplete=get_aliases)):

        if await Tags.is_staff(self, ctx):
            loading = EMOTES["loading"]
            embed = discord.Embed(
                description=f"{loading} Working on it....", color=COLORS["info"])

            await ctx.respond(embed=embed)
            message = await ctx.interaction.original_message()

            collection = self.bot.database["tags"]
            name = name.lower()
            alias = alias.lower()
            check = {"name": name}

            find = collection.find_one(check)
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

                        aliases = {"$set": {
                            "aliases": newAliases, "lastUpdateAt": updatedTime, "lastUpdateBy": ctx.author.id}}

                        collection.update_one(check, aliases)

                        success = EMOTES["success"]
                        embed = discord.Embed(
                            description=f"{success} **Added** alias: {alias}", color=COLORS["success"], timestamp=datetime.datetime.utcnow())
                        await message.edit(embed=embed)

                    else:
                        x = EMOTES["error"]
                        embed = discord.Embed(
                            description=f"{x} This alias already exists", color=COLORS["error"])
                        await message.edit(embed=embed)

                elif choice == "remove":
                    aliases = find["aliases"]

                    try:
                        newAlias = aliases
                        newAlias.remove(alias)
                        if len(newAlias) == 0:
                            aliases.append("None")

                        update = {"$set": {
                            "aliases": aliases, "lastUpdateAt": updatedTime, "lastUpdateBy": ctx.author.id}}
                        collection.update_one(check, update)

                        success = EMOTES["success"]
                        embed = discord.Embed(
                            description=f"{success} **Removed** alias: {alias}", color=COLORS["success"], timestamp=datetime.datetime.utcnow())
                        await message.edit(embed=embed)

                    except Exception:
                        x = EMOTES["error"]
                        embed = discord.Embed(
                            description=f"{x} No alias found for this tag", color=COLORS["error"])
                        await message.edit(embed=embed)

                else:
                    await message.edit("Invalid typeAlias selected.")
            else:
                x = EMOTES["error"]
                embed = discord.Embed(
                    description=f"{x} No tag found by this name", color=COLORS["error"])
                await message.edit(embed=embed)

        else:
            x = EMOTES["error"]
            embed = discord.Embed(
                description=f"{x} You do not have permission to run this command.", color=COLORS["error"])
            await ctx.respond(embed=embed, ephemeral=True)

    @tags.command(description="Get a tags list and a paginator")
    @commands.cooldown(1, 5, commands.BucketType.default)
    async def all(self, ctx: discord.ApplicationContext):

        await ctx.defer()

        collection = self.bot.database["tags"]
        pagPages = []
        tags = []

        for tag in collection.find():
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
            find = collection.find_one(check)

            name = find["name"]
            aliases = ", ".join(find["aliases"])
            content = find["content"]
            author = self.bot.get_user(find["author"])
            createdAt = find["createdAt"]
            lastUpdateAt = find["lastUpdateAt"]
            lastUpdateBy = self.bot.get_user(find["lastUpdateBy"])

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
    async def send(self, ctx: discord.ApplicationContext, name: Option(str, "The tag you want to display", autocomplete=get_tags_and_alias), text: Option(str, "Optional text before the tag (usually mentions)", required=False, default=None)):

        await ctx.defer()
        name = name.lower()

        collection = self.bot.database["tags"]

        check = {"name": name}
        find = collection.find_one(check)
        if not find:
            check = {"aliases": name}
            find = collection.find_one(check)

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
