from datetime import datetime

import aiohttp
import discord
from discord.ext import commands

from resources.CheckFailure import is_blacklisted, is_staff
from config import colors, links


class GroupApiCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def parse_input(self, group: str) -> str:
        result = ""

        if "/groups/" in group:
            # Roblox URL, grab ID.
            split = group.split("/groups/")
            split_two = split[1].split("/", maxsplit=1)
            result = split_two[0]
        elif group.isdigit():
            # Check if the input is a valid number
            result = group

        return result

    @commands.command(aliases=["gapi", "groups"])
    @commands.guild_only()
    @is_blacklisted()
    @is_staff()
    async def group(self, ctx: commands.Context, *, group_id: str):
        embed = discord.Embed(color=colors.info, timestamp=datetime.utcnow())

        group_id = self.parse_input(group_id)
        INFO_URL = f"/v1/groups/{group_id}"
        RANK_URL = f"{INFO_URL}/roles"

        if group_id:
            session = aiohttp.ClientSession("https://groups.roblox.com")
            info_data: dict | None = None
            rank_data: dict | None = None

            async with session.get(INFO_URL) as info_req:
                info_data = await info_req.json()
            async with session.get(RANK_URL) as rank_req:
                rank_data = await rank_req.json()

            await session.close()

            desc_builder = []

            name = "Invalid group."
            members = 0
            owner = "N/A"

            error_check = info_data.get("errors", None)
            if error_check:
                info_data = None
                rank_data = None

            if info_data:
                name = info_data.get("name", name)
                members = info_data.get("memberCount", 0)

                owner_data = info_data.get("owner", {})
                owner = owner_data.get("username", owner)

            desc_builder.append(f"> **Name:** {name}")
            desc_builder.append(f"> **Owner:** {owner}")
            desc_builder.append(f"> **Member Count:** {members}")
            desc_builder.append(" ")

            if rank_data:
                desc_builder.append(f"**Group Ranks:**")

                ranks = rank_data.get("roles", [])
                for rank in ranks:
                    rank_name = rank.get("name", "Invalid Name")
                    rank_id = rank.get("rank", -1)
                    desc_builder.append(f"- `{rank_id:3d}`: {rank_name}")

            embed.set_author(
                icon_url=links.success,
                name="Successfully sent request",
            )
            embed.description = "\n".join(desc_builder)
        else:
            return await ctx.error("Invalid group ID.")

        await ctx.reply(embed=embed, mention_author=False)


def setup(bot):
    bot.add_cog(GroupApiCommand(bot))
