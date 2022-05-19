import discord
from discord.ui import InputText, Modal

import time
import datetime
from config import EMOTES, LINKS, COLORS


class TagCreateModal(Modal):
    def __init__(self, bot, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.bot = bot

        self.add_item(InputText(label="Tag Name", placeholder="Type the tag name here", style=discord.InputTextStyle.short))

        self.add_item(InputText(label="Tag Aliases", placeholder="Type the tag aliases here, separate them with a comma", style=discord.InputTextStyle.short, value="None", required=False))

        self.add_item(InputText(label="Tag Content", placeholder="Type the tag content here", style=discord.InputTextStyle.long))

    async def callback(self, interaction: discord.Interaction):

        collection = self.bot.database["tags"]
        createdAt = round(time.time() * 1)
        name = self.children[0].value.lower()
        aliases = self.children[1].value
        aliases = aliases.lower() if aliases != "None" else None
        aliases = aliases.replace(
            " ", "") if aliases is not None else aliases
        aliases = aliases.split(",") if aliases is not None else ["None"]
        content = self.children[2].value.replace("\\n", "\n")

        newTag = {"name": name, "aliases": aliases, "content": content, "author": interaction.user.id,
                    "lastUpdateBy": interaction.user.id, "createdAt": createdAt, "lastUpdateAt": createdAt}
        check = {"name": name}
        check2 = {"aliases": aliases}
        find2 = collection.find_one(
            check2) if aliases[0] != "None" else False

        if collection.find_one(check) or find2:
            error = EMOTES["error"]
            embed = discord.Embed(
                description=f"{error} A tag with that name/alias already exists!", color=COLORS["error"])
            await interaction.response.send_message(embed=embed)

        else:
            item = collection.insert_one(newTag)
            aliases = ", ".join(aliases)

            embed = discord.Embed(
                title=f":paperclips: Aliases: {aliases}", description=f":page_with_curl: Tag content:\n{content}", color=COLORS["success"], timestamp=datetime.datetime.utcnow())
            embed.set_footer(
                icon_url=LINKS["other"], text=f"Item ID: {item.inserted_id}")
            embed.set_author(
                icon_url=LINKS["success"], name=f"Successfully created tag: {name}")

            await interaction.response.send_message(embed=embed)

class TagEditModal(Modal):
    def __init__(self, bot, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.bot = bot

        self.add_item(InputText(label="Tag Name", placeholder="Type the tag name here", style=discord.InputTextStyle.short))
        self.add_item(InputText(label="Tag Content", placeholder="Type the new tag content here", style=discord.InputTextStyle.long))

    async def callback(self, interaction: discord.Interaction):
        collection = self.bot.database["tags"]
        name = self.children[0].value.lower()
        content = self.children[1].value.replace("\\n", "\n")

        check = {"name": name}
        find = collection.find_one(check)

        if find:
            item = collection.find_one_and_update(
                check, {"$set": {"content": content, "lastUpdateBy": interaction.user.id, "lastUpdateAt": round(time.time() * 1)}})
            embed = discord.Embed(
                description=f":page_with_curl: New tag content:\n{content}", color=COLORS["success"], timestamp=datetime.datetime.utcnow())
            embed.set_author(
                icon_url=LINKS["success"], name=f"Successfully updated tag: {name}")

            await interaction.response.send_message(embed=embed)

        else:
            error = EMOTES["error"]
            embed = discord.Embed(
                description=f"{error} A tag with that name does not exist!", color=COLORS["error"])
            await interaction.response.send_message(embed=embed)