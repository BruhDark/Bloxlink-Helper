import datetime

import discord
from config import badges, emotes, colors
from discord.commands import Option, slash_command
from discord.ext import commands

from resources.CheckFailure import is_blacklisted


class Whois(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.description = "Get information about an user"
        self.category = "Miscellaneous"

    @slash_command()
    @commands.guild_only()
    @is_blacklisted()
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def whois(self, ctx: commands.Context, member: Option(discord.Member, "Specify a user", required=False, default=None)):
        """Get information about an user."""

        if member == None:
            id = ctx.author.id
        elif type(member) == int:
            id = member
        else:
            id = member.id

        user = ctx.guild.get_member(id)
        noMember = False

        if user == None:
            user = await self.bot.fetch_user(id)
            noMember = True

        if not noMember:
            roles = [role.mention for role in user.roles[1:]]
            roles.reverse()

            if len(roles) == 0:
                roles = None
        else:
            roles = None

        if not noMember:
            joined = int(user.joined_at.timestamp())

        if not noMember:
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

        color = user.color if not noMember else colors.info
        if user.id == self.bot.user.id:
            color = colors.info

        amember = "**This user is not a member of this server.**" if noMember else ""
        nickname = f"**Nickname:** {user.display_name}" if not noMember else ""

        Embed = discord.Embed(color=color, timestamp=datetime.datetime.utcnow(
        ), description=f"{user.mention}\n{nickname}\n{amember}")

        Embed.set_author(
            name=f"{user.name}#{user.discriminator}", icon_url=user.display_avatar.url)

        bloxlinkGuild = self.bot.get_guild(372036754078826496)
        bloxlinkUser = discord.utils.get(bloxlinkGuild.members, id=user.id)
        staffRole = discord.utils.get(
            bloxlinkGuild.roles, id=889927613580189716)

        if bloxlinkUser is not None and staffRole in bloxlinkUser.roles:
            Embed.set_thumbnail(
                url="https://i.imgur.com/Fcndmhh.png")  # staff shield

        else:
            Embed.set_thumbnail(url=user.display_avatar.url)

        if not noMember:
            Embed.add_field(name="Status", value=status, inline=False)

        Embed.add_field(name="Registered",
                        value=f"<t:{int(user.created_at.timestamp())}:R> (<t:{int(user.created_at.timestamp())}:f>)", inline=True)

        if not noMember:
            Embed.add_field(name="Joined",
                            value=f"<t:{joined}:R> (<t:{joined}:f>)", inline=True)

        if roles is not None:
            Embed.add_field(name="Highest Role", value=user.top_role.mention)

            Embed.add_field(
                name=f"Roles [{len(roles)}]", value=", ".join(roles), inline=False)

        flags = []

        if user.public_flags.staff:
            flags.append(f"{badges.staff} Discord Staff")

        if user.public_flags.partner:
            flags.append(f"{badges.partner} Partnered Server Owner")

        if user.public_flags.discord_certified_moderator:
            flags.append(f"{badges.moderator} Discord Certified Moderator")

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

        if len(flags) == 0:
            flags.append("None")

        if "None" not in flags:
            Embed.add_field(name="Profile Badges",
                            value="\n".join(flags), inline=False)

        acks = []
        helperRole = discord.utils.get(
            bloxlinkGuild.roles, id=412791520316358656)
        modRole = discord.utils.get(bloxlinkGuild.roles, id=372174398918098944)
        cmRole = discord.utils.get(bloxlinkGuild.roles, id=595733840849534982)
        devRole = discord.utils.get(bloxlinkGuild.roles, id=539665515430543360)

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
            acks = None

        if acks is not None:
            Embed.add_field(name="Bloxlink Team",
                            value=", ".join(acks), inline=False)

        Embed.set_footer(text=f"ID: {user.id}")

        await ctx.respond(embed=Embed)

    @commands.command(aliases=["w", "userinfo"])
    @commands.guild_only()
    @is_blacklisted()
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def whois(self, ctx: commands.Context, *, member: str = None):
        """Get information about an user."""

        if member is None:
            user = ctx.author
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
                    raise e
                user = await self.bot.fetch_user(id)
                noMember = True

        if not noMember:
            roles = [role.mention for role in user.roles[1:]]
            roles.reverse()

            if len(roles) == 0:
                roles = None
        else:
            roles = None

        if not noMember:
            joined = int(user.joined_at.timestamp())

        if not noMember:
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

        color = user.color if not noMember else colors.info
        if user.id == self.bot.user.id:
            color = colors.info

        nickname = f"**Nickname:** {user.display_name}" if not noMember and user.name != user.display_name else ""
        amember = f"**This user is not a member of this server.**\n{nickname}" if noMember else nickname

        Embed = discord.Embed(color=color, timestamp=datetime.datetime.utcnow(
        ), description=f"{user.mention}\n{nickname}\n{amember}")

        Embed.set_author(
            name=f"{user.name}#{user.discriminator}", icon_url=user.display_avatar.url)

        bloxlinkGuild = self.bot.get_guild(372036754078826496)
        bloxlinkUser = discord.utils.get(bloxlinkGuild.members, id=user.id)
        staffRole = discord.utils.get(
            bloxlinkGuild.roles, id=889927613580189716)

        if bloxlinkUser is not None and staffRole in bloxlinkUser.roles:
            Embed.set_thumbnail(
                url="https://i.imgur.com/Fcndmhh.png")  # staff shield

        else:
            Embed.set_thumbnail(url=user.display_avatar.url)

        if not noMember:
            Embed.add_field(name="Status", value=status, inline=False)

        Embed.add_field(name="Registered",
                        value=f"<t:{int(user.created_at.timestamp())}:R> (<t:{int(user.created_at.timestamp())}:f>)", inline=True)

        if not noMember:
            Embed.add_field(name="Joined",
                            value=f"<t:{joined}:R> (<t:{joined}:f>)", inline=True)

        if roles is not None:
            Embed.add_field(name="Highest Role", value=user.top_role.mention)

            Embed.add_field(
                name=f"Roles [{len(roles)}]", value=", ".join(roles), inline=False)

        flags = []

        if user.public_flags.staff:
            flags.append(f"{badges.staff} Discord Staff")

        if user.public_flags.partner:
            flags.append(f"{badges.partner} Partnered Server Owner")

        if user.public_flags.discord_certified_moderator:
            flags.append(f"{badges.moderator} Discord Certified Moderator")

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

        if len(flags) == 0:
            flags.append("None")

        if "None" not in flags:
            Embed.add_field(name="Profile Badges",
                            value="\n".join(flags), inline=False)

        acks = []
        helperRole = discord.utils.get(
            bloxlinkGuild.roles, id=412791520316358656)
        modRole = discord.utils.get(bloxlinkGuild.roles, id=372174398918098944)
        cmRole = discord.utils.get(bloxlinkGuild.roles, id=595733840849534982)
        devRole = discord.utils.get(bloxlinkGuild.roles, id=539665515430543360)

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
            acks = None

        if acks is not None:
            Embed.add_field(name="Bloxlink Team",
                            value=", ".join(acks), inline=False)

        Embed.set_footer(text=f"ID: {user.id}")

        await ctx.send(embed=Embed)


def setup(bot):
    bot.add_cog(Whois(bot))
