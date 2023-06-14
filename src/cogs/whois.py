import datetime

import discord
from config import badges, emotes, colors
from discord.commands import Option, slash_command
from discord.ext import commands

from resources.CheckFailure import is_blacklisted


class Whois(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot
        self.description = "Get information about an user"
        self.category = "Miscellaneous"

    async def get_badges(self, user: discord.Member | discord.User) -> list:
        flags = []
        if user.public_flags.staff:
            flags.append(f"{badges.staff} Discord Staff")

        if user.public_flags.partner:
            flags.append(f"{badges.partner} Partnered Server Owner")

        if user.public_flags.discord_certified_moderator:
            flags.append(f"{badges.moderator} Discord Certified Moderator")

        if user.public_flags.active_developer:
            flags.append(f"{badges.active_developer} Active Developer")

        if user.public_flags.verified_bot_developer or user.public_flags.early_verified_bot_developer:
            flags.append(f"{badges.botdev} Verified Bot Developer")

        if user.public_flags.bug_hunter:
            flags.append(f"{badges.bughunter} Bug Hunter")

        if user.public_flags.bug_hunter_level_2:
            flags.append(f"{badges.bughunter2} Bug Hunter")

        if user.public_flags.early_supporter:
            flags.append(f"{badges.early} Early Supporter")

        if user.public_flags.hypesquad:
            flags.append(f"{badges.events} Hypesquad Events")

        if user.public_flags.hypesquad_bravery:
            flags.append(f"{badges.bravery} Hypesquad Bravery")

        elif user.public_flags.hypesquad_brilliance:
            flags.append(f"{badges.brilliance} Hypesquad Brilliance")

        elif user.public_flags.hypesquad_balance:
            flags.append(f"{badges.balance} Hypesquad Balance")

        if user.bot:
            flags.append(f"{badges.bot} Bot")

        if user.public_flags.verified_bot:
            flags.append(f"{badges.verifiedbot} Verified Bot")

        if user.is_migrated:
            flags.append(f"{badges.old_username} Migrated Username")

        if len(flags) == 0:
            return None
        return flags

    async def get_activity(self, user: discord.Member | discord.User):
        activity_name = user.activity.name
        activity_emoji = user.activity.emoji if user.activity.type == discord.ActivityType.custom and user.activity.emoji is not None else ""

        if activity_name == None:
            for activity in user.activities:
                if activity.name is not None:
                    activity_name = activity.name
                    break
            else:
                activity_name = ""

        if user.activity.type == discord.ActivityType.custom and user.activity.name is not None:
            activity_type = ""

        elif user.activities[0].type == discord.ActivityType.listening or (user.activities[1].type == discord.ActivityType.listening if len(user.activities) > 1 else False):
            activity_type = "Listening to "

        elif user.activities[0].type == discord.ActivityType.playing or (user.activities[1].type == discord.ActivityType.playing if len(user.activities) > 1 else False):
            activity_type = "Playing "

        elif user.activities[0].type == discord.ActivityType.watching or (user.activities[1].type == discord.ActivityType.watching if len(user.activities) > 1 else False):
            activity_type = "Watching "

        elif user.activities[0].type == discord.ActivityType.streaming or (user.activities[1].type == discord.ActivityType.streaming if len(user.activities) > 1 else False):
            activity_type = "Streaming "

        else:
            activity_type = ""

        return f"{activity_emoji} {activity_type} {activity_name}".strip(
        )

    async def get_acks(self, user: discord.Member | discord.User):

        acks = []
        bloxlinkGuild = self.bot.get_guild(372036754078826496)
        helperRole = bloxlinkGuild.get_role(412791520316358656)
        modRole = bloxlinkGuild.get_role(372174398918098944)
        cmRole = bloxlinkGuild.get_role(595733840849534982)
        devRole = bloxlinkGuild.get_role(539665515430543360)

        bloxlinkUser = bloxlinkGuild.get_member(user.id)
        staffRole = bloxlinkGuild.get_role(889927613580189716)

        if bloxlinkUser is not None and staffRole in bloxlinkUser.roles:
            acks.append("Staff")

        if bloxlinkUser is not None and helperRole in bloxlinkUser.roles:
            acks.append("Helper")

        if bloxlinkUser is not None and modRole in bloxlinkUser.roles:
            acks.append("Moderator")

        if bloxlinkUser is not None and cmRole in bloxlinkUser.roles:
            acks.append("Community Manager")

        if bloxlinkUser is not None and devRole in bloxlinkUser.roles:
            acks.append("Developer")

        if len(acks) == 0:
            return None
        return acks

    async def get_status(self, user: discord.Member):
        x = user.raw_status
        if x == "online":
            status = emotes.online

        elif x == "idle":
            status = emotes.idle

        elif x == "dnd":
            status = emotes.dnd

        elif x == "offline":
            status = emotes.offline

        else:
            status = emotes.question

        return status

    @commands.command(aliases=["w", "userinfo"])
    @commands.guild_only()
    @is_blacklisted()
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def whois(self, ctx: commands.Context, *, member: str = None):
        """Get information about an user."""
        async with ctx.typing():

            # Attempt to get member
            if member is None:
                user: discord.Member = ctx.author
                noMember = False
            else:
                try:
                    converter = commands.MemberConverter()
                    user = await converter.convert(ctx, member)
                    noMember = False

                except Exception as e:
                    try:
                        id = int(member)
                    except:
                        raise commands.MemberNotFound

                    user: discord.User = await self.bot.fetch_user(id)
                    noMember = True

            # Process and get all possible fields of information

            # Embed color
            color = user.color if not noMember else colors.info
            if user.id == self.bot.user.id:
                color = colors.info

            # User nickname and if in server
            nickname = f"**Nickname:** {user.display_name}" if not noMember and user.name != user.display_name else ""
            nickname = f"**This user is not a member of this server.**\n{nickname}" if noMember else nickname

            # Create embed
            embed = discord.Embed(color=color, timestamp=datetime.datetime.utcnow(
            ), description=f"{user.mention}\n{nickname}")

            embed.set_author(
                name=f"{user.name}#{user.discriminator}" if user.discriminator != "0" else user.name, icon_url=user.display_avatar.url)

            # See if they are staff, if so, apply a custom thumbnail otherwise their avatar
            bloxlinkGuild = self.bot.get_guild(372036754078826496)
            bloxlinkUser = bloxlinkGuild.get_member(user.id)
            staffRole = bloxlinkGuild.get_role(889927613580189716)

            if bloxlinkUser is not None and staffRole in bloxlinkUser.roles:
                embed.set_thumbnail(
                    url="https://i.imgur.com/Fcndmhh.png")  # staff shield

            else:
                embed.set_thumbnail(url=user.display_avatar.url)

            # Add activity field if it activity exists
            if not noMember and user.activity:
                embed.add_field(name="Status", value=await self.get_status(user), inline=True)
                embed.add_field(name="Activity",
                                value=await self.get_activity(user), inline=True)

            # Add registered field
            embed.add_field(name="Registered",
                            value=f"<t:{int(user.created_at.timestamp())}:R> (<t:{int(user.created_at.timestamp())}:f>)", inline=True)

            # Add fields for roles, joined, status, roles
            if not noMember:
                joined = int(user.joined_at.timestamp())
                embed.add_field(name="Joined",
                                value=f"<t:{joined}:R> (<t:{joined}:f>)", inline=True)

                roles = [role.mention for role in user.roles[1:]]
                roles.reverse()
                roles = None if len(roles) == 0 else roles
                if roles is not None:
                    embed.add_field(name="Highest Role",
                                    value=user.top_role.mention, inline=True)
                    embed.add_field(
                        name=f"Roles [{len(roles)}]", value=", ".join(roles), inline=False)

            badges = await self.get_badges(user)

            if badges is not None:
                embed.add_field(name="Profile Badges",
                                value="\n".join(badges), inline=False)

            acks = await self.get_acks(user)
            if acks is not None:
                embed.add_field(name="Bloxlink Team",
                                value=", ".join(acks), inline=False)

            embed.set_footer(text=f"ID: {user.id}")

        await ctx.reply(embed=embed, mention_author=False)


def setup(bot):
    bot.add_cog(Whois(bot))
