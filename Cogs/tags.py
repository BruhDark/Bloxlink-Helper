import discord
from discord.ext import commands, pages
from discord.commands import slash_command, Option, permissions
import pymongo
import time
import datetime
from config import COLORS, EMOTES, RELEASESCOLORS, LINKS
import asyncio

class Tags(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.database = self.bot.database

    tags = discord.SlashCommandGroup("tag", "Tag related commands.")

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
    
    @tags.command(description="Create a new tag", default_permission=False)
    @permissions.has_any_role("Staff")
    async def create(self, ctx: discord.ApplicationContext, name: Option(str, "The new tag name"), content: Option(str, "The tag content"), aliases: Option(str, "Aliases for this tag, separated by a comma, no space", required=False, default=None)):

        collection =  self.bot.database["tags"]
        createdAt = round(time.time() * 1)
        name = name.lower()
        aliases = aliases.lower() if aliases is not None else aliases
        aliases = aliases.replace(" ", "") if aliases is not None else aliases
        aliases = aliases.split(",") if aliases is not None else ["None"]
        content = content.replace("\\n", "\n")

        loading = EMOTES["loading"]
        embed = discord.Embed(description=f"{loading} Working on it....", color=COLORS["info"])

        await ctx.respond(embed=embed)
        message = await ctx.interaction.original_message()
        
        newTag = {"name": name, "aliases": aliases,"uses": 0,"content": content, "author":ctx.author.id, "lastUpdateBy": ctx.author.id,"createdAt": createdAt, "lastUpdateAt": createdAt}
        check = {"name": name}
        check2 = {"aliases": aliases}
        find2 = collection.find_one(check2) if aliases[0] != "None" else False

        if collection.find_one(check) or find2:
            error = EMOTES["error"]
            embed = discord.Embed(description=f"{error} A tag with that name/alias already exists!", color=COLORS["error"])
            await message.edit(embed=embed)

        else:
            item = collection.insert_one(newTag)

            embed = discord.Embed(description=f":page_with_curl: Tag content:\n{content}", color=COLORS["success"], timestamp=datetime.datetime.utcnow())
            embed.set_footer(icon_url=ctx.author.avatar.url, text=f"{ctx.author.name}#{ctx.author.discriminator}")
            embed.add_field(name=":clipboard: Tag Name", value=name, inline=True)
            embed.add_field(name=":paperclips: Alias(es)", value=", ".join(aliases), inline=True)
            embed.add_field(name=":microscope: Item ID", value=item.inserted_id, inline=False)

            embed.set_author(icon_url=LINKS["success"], name=f"Successfully created a new tag")
            
            await message.edit(embed=embed)

    @tags.command(description="Remove an existent tag", default_permission=False)
    @permissions.has_any_role("Staff")
    async def remove(self, ctx: discord.ApplicationContext, name: Option(str, "The tag name you wish to remove", autocomplete=get_tags)):

        collection = self.bot.database["tags"]
        name = name.lower()
        check = {"name": name}
        
        loading = EMOTES["loading"]
        embed = discord.Embed(description=f"{loading} Working on it....", color=COLORS["info"])
        await ctx.respond(embed=embed)
        message = await ctx.interaction.original_message()

        find = collection.find_one(check)

        if find:
            
            query = {"name": name}
            oldContent = find["content"]
            createdBy = find["author"]
            id = find["_id"]

            collection.delete_one(query)

            embed = discord.Embed(description=f":page_with_curl: Old Tag Content:\n{oldContent}", color=COLORS["warning"], timestamp=datetime.datetime.utcnow())
            embed.add_field(name=":wastebasket: Deleted Tag Name", value=name, inline=True)
            embed.add_field(name=":bust_in_silhouette: Created By", value=f"<@{createdBy}>", inline=True)
            embed.add_field(name=":microscope: Deleted Item ID", value=id, inline=False)
            embed.set_footer(icon_url=ctx.author.avatar.url, text=f"{ctx.author.name}#{ctx.author.discriminator}")
            embed.set_author(icon_url=LINKS["success"], name=f"Successfully deleted this tag")

            await message.edit(embed=embed)

        else:
            x = EMOTES["error"]
            embed = discord.Embed(description=f"{x} A tag with that name does not exist!", color=COLORS["error"])
            await message.edit(embed=embed)

    @tags.command(description="Get information about a tag")
    async def info(self, ctx: discord.ApplicationContext, name: Option(str, "Search by name or alias", autocomplete=get_tags_and_alias)):

        collection = self.bot.database["tags"]
        name = name.lower()
        check = {"name": name}
        check2 = {"aliases": name}

        loading = EMOTES["loading"]
        embed = discord.Embed(description=f"{loading} Working on it....", color=COLORS["info"])
        await ctx.respond(embed=embed)
        message = await ctx.interaction.original_message()

        find = collection.find_one(check)
        find2 = collection.find_one(check2)

        if find or find2:

            name = find["name"]
            author = self.bot.get_user(find["author"])
            lastUpdateBy = self.bot.get_user(find["lastUpdateBy"])
            uses = find["uses"]
            createdAt = find["createdAt"]
            lastUpdateAt = find["lastUpdateAt"]
            aliases = find["aliases"]
            aliases = ", ".join(aliases) if aliases != "None" else "None"
            content = find["content"]


            embed = discord.Embed(description=f":page_with_curl: Tag content:\n{content}", color=COLORS["success"], timestamp=datetime.datetime.utcnow())
            embed.set_author(icon_url=LINKS["success"], name=f"Found a match for: {name}")
            embed.add_field(name=":brain: Author", value=f"{author.mention} ({author.id})")
            embed.add_field(name=":hourglass_flowing_sand: Last Update By", value=f"{lastUpdateBy.mention} ({lastUpdateBy.id})")
            embed.add_field(name=":arrows_counterclockwise: Uses", value=uses)
            embed.add_field(name=":paperclips: Aliases", value=aliases)
            embed.add_field(name=":calendar: Creation Date", value=f"<t:{createdAt}:R>")
            embed.add_field(name=":timer: Last Update", value=f"<t:{lastUpdateAt}:R>")

            await message.edit(embed=embed)

        else:
            x = EMOTES["error"]
            embed = discord.Embed(description=f"{x} No tag found by this name", color=COLORS["error"])
            await message.edit(embed=embed)

    @tags.command(description="Get the raw content of a tag", default_permission=False)
    @permissions.has_any_role("Staff")
    async def raw(self, ctx: discord.ApplicationContext, name: Option(str, "The tag name to get the raw content from", autocomplete=get_tags_and_alias)):
        
        collection = self.bot.database["tags"]
        name = name.lower()

        loading = EMOTES["loading"]
        embed = discord.Embed(description=f"{loading} Working on it....", color=COLORS["info"])
        await ctx.respond(embed=embed)
        message = await ctx.interaction.original_message()
        check = {"name": name}
        check2 = {"aliases": name}

        find  = collection.find_one(check)
        find2 = collection.find_one(check2)

        if find or find2:

            content = find["content"]

            embed = discord.Embed(description=f":page_with_curl: Raw content:\n```\n{content}```", color=COLORS["success"], timestamp=datetime.datetime.utcnow())
            embed.set_author(icon_url=LINKS["success"], name=f"Found a match. Raw content for: {name}")
            
            await message.edit(embed=embed)
            await ctx.send(f":mobile_phone: For mobile users:\n```\n{content}```")

        else:
            x = EMOTES["error"]
            embed = discord.Embed(description=f"{x} No tag found by this name", color=COLORS["error"])
            await message.edit(embed=embed)

    @tags.command(description="Edit an existent tag's content", default_permission=False)
    @permissions.has_any_role("Staff")
    async def edit(self, ctx: discord.ApplicationContext, name: Option(str, "The tag name you want to edit", autocomplete=get_tags), content: Option(str, "The new content for this tag")):

        loading = EMOTES["loading"]
        embed = discord.Embed(description=f"{loading} Working on it....", color=COLORS["info"])
        await ctx.respond(embed=embed)
        message = await ctx.interaction.original_message()

        collection = self.bot.database["tags"]
        name = name.lower()
        check = {"name": name}

        find = collection.find_one(check)

        if find:

            oldContent = find["content"]

            updatedTime = round(time.time() * 1)
            update = {"$set": {"content": content,"lastUpdateAt": updatedTime, "lastUpdateBy": ctx.author.id}}
            collection.update_one(check, update)

            
            embed = discord.Embed(description=f":page_with_curl: New content:\n{content}\n\n:wastebasket: Old content:\n{oldContent}", color=COLORS["success"], timestamp=datetime.datetime.utcnow())
            embed.set_author(icon_url=LINKS["success"], name=f"Done! Successfully edited: {name}")
            await message.edit(embed=embed)
        
        else:
            x = EMOTES["error"]
            embed = discord.Embed(description=f"{x} No tag found by this name", color=COLORS["error"])
            await message.edit(embed=embed)

    @tags.command(description="Add or remove tag aliases", default_permission=False)
    @permissions.has_any_role("Staff")
    async def alias(self, ctx: discord.ApplicationContext, name: Option(str, "The tag name you wish to edit its alias", autocomplete=get_tags), choice: Option(str, "Add or remove an alias?", choices=["add", "remove"]), alias: Option(str, "New alias or alias to be removed", autocomplete=get_aliases)):

        loading = EMOTES["loading"]
        embed = discord.Embed(description=f"{loading} Working on it....", color=COLORS["info"])
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
                 if oldAliases[0] == "None":
                     newAliases.remove("None")

                 aliases = {"$set": {"aliases": newAliases, "lastUpdateAt": updatedTime, "lastUpdateBy": ctx.author.id}}

                 collection.update_one(check, aliases)


                 embed = discord.Embed(color=COLORS["success"], timestamp=datetime.datetime.utcnow())
                 embed.set_author(icon_url=LINKS["success"], name=f"Done! Successfully edited {name}'s aliases")
                 embed.add_field(name=":older_man: Old Aliases", value=", ".join(find["aliases"]))
                 embed.add_field(name=":baby: New Aliases", value=", ".join(newAliases))

                 await message.edit(embed=embed)

                else:
                    x = EMOTES["error"]
                    embed = discord.Embed(description=f"{x} This alias already exists", color=COLORS["error"])
                    await message.edit(embed=embed)
            
            elif choice == "remove":
                aliases = find["aliases"]

                try:
                    newAlias = aliases
                    newAlias.remove(alias)
                    if len(newAlias) == 0:
                        aliases.append("None")
                    
                    update = {"$set": {"aliases": aliases, "lastUpdateAt": updatedTime, "lastUpdateBy": ctx.author.id}}
                    collection.update_one(check, update)

                    embed = discord.Embed(color=COLORS["success"], timestamp=datetime.datetime.utcnow())
                    embed.set_author(icon_url=LINKS["success"], name=f"Done! Successfully edited {name}'s aliases")
                    embed.add_field(name=":older_man: Old Aliases", value=", ".join(aliases))
                    embed.add_field(name=":baby: New Aliases", value=", ".join(newAlias))

                except Exception:
                    x = EMOTES["error"]
                    embed = discord.Embed(description=f"{x} No alias found for this tag", color=COLORS["error"])
                    await message.edit(embed=embed)
            
            else:
                await message.edit("Invalid typeAlias selected.")
        else:
            x = EMOTES["error"]
            embed = discord.Embed(description=f"{x} No tag found by this name", color=COLORS["error"])
            await message.edit(embed=embed)

    @tags.command(description="Get a tags list and a paginator")
    async def all(self, ctx: discord.ApplicationContext):

        await ctx.defer()

        collection = self.bot.database["tags"]
        pagPages = []
        tags = []

        for tag in collection.find():
            tags.append(tag["name"])

        tags.sort()

        tagsEmbed = discord.Embed(description=", ".join(tags), color=COLORS["info"], timestamp=datetime.datetime.utcnow())
        emote = LINKS["other"]
        tagsEmbed.set_author(icon_url=emote, name="Listing all tags:")
        tagsEmbed.set_footer(text="Use the paginator to go over the tags. Oldest -> Newest")
        pagPages.append(tagsEmbed)

        for tag in collection.find():
            name = tag["name"]
            aliases = ", ".join(tag["aliases"])
            uses = tag["uses"]
            content = tag["content"]
            author = self.bot.get_user(tag["author"])
            createdAt = tag["createdAt"]
            lastUpdateAt = tag["lastUpdateAt"]

            embed = discord.Embed(description=f":page_with_curl: Tag content:\n{content}", timestamp=datetime.datetime.utcnow(), color=COLORS["info"])
            embed.set_author(icon_url=author.display_avatar.url, name=f"Created by: {author.name}")
            embed.add_field(name=":clipboard: Name", value=name)
            embed.add_field(name=":paperclips: Aliases", value=aliases)
            embed.add_field(name=":arrows_counterclockwise: Uses", value=uses)
            embed.add_field(name=":calendar: Creation Date", value=f"<t:{createdAt}:R>")
            embed.add_field(name=":timer: Last Update", value=f"<t:{lastUpdateAt}:R>")

            pagPages.append(embed)

        paginator = pages.Paginator(pages=pagPages, disable_on_timeout=True, timeout=60, show_disabled=False)
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

            uses = find["uses"]
            update = {"$set": {"uses": uses + 1}}
            collection.update_one(check, update)

        else:
            x = EMOTES["error"]
            embed = discord.Embed(description=f"{x} No tag matching your search.", color=COLORS["error"])
            await ctx.respond(embed=embed, delete_after=5.0)

    @commands.command()
    async def tag(self, ctx: discord.ApplicationContext, name: str, *, text: str = None):

        name = name.lower()

        collection = self.bot.database["tags"]

        check = {"name": name}
        find = collection.find_one(check)
        if not find:
            check = {"aliases": name}
            find = collection.find_one(check)

        text = text if text is not None else None

        if find:
            if text is not None:
                await ctx.message.delete()
                
                tag = find["content"]

                msg = await ctx.send(f"{tag}")
                asyncio.sleep(0.1)
                await msg.edit(f"{text} {tag}")


                uses = find["uses"]
                update = {"$set": {"uses": uses + 1}}
                collection.update_one(check, update)

            else:
                await ctx.message.delete()
                
                tag = find["content"]

                await ctx.send(f"{tag}")

                uses = find["uses"]
                update = {"$set": {"uses": uses + 1}}
                collection.update_one(check, update)


        else:
            await ctx.message.delete()
            x = EMOTES["error"]
            embed = discord.Embed(description=f"{x} No tag matching your search.", color=COLORS["error"])
            await ctx.send(embed=embed, delete_after=5.0)


def setup(bot):
    bot.add_cog(Tags(bot))