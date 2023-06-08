import discord

PREFIX = "."
DESCRIPTION = "Bloxlink HQ's tags bot."

AUTHORIZED = [449245847767482379, 431480956990390272, 156872400145874944]


class Emotes:
    def __init__(self):
        self.success = "<:BloxlinkHappy:823633735446167552>"
        self.error: str = "<:BloxlinkDead:823633973967716363>"
        self.success2: str = "<a:BHDone:976817167116947507>"
        self.warning = ":warning:"
        self.info = "<:info:881973831974154250>"
        self.question = "<:BloxlinkConfused:823633690910916619>"
        self.operational = "<:Operational:882404710148083724>"
        self.partialoutage = "<:PartialOutage:882404755949895730>"
        self.majoroutage = "<:MajorOutage:882404641286000681>"
        self.owner = "<:owner:881973891017355344>"

        self.dnd = "<:DoNotDisturb:928716110822518834>"
        self.idle = "<:Idle:929049988573581352>"
        self.online = "<:Online:928716318054694993>"
        self.offline = "<:Offline:928716879474851870>"

        self.loading = "<a:loading:946809583194767400>"
        self.spotify = "<:Spotify:929060525881565224>"
        self.bloxlink = "<:BloxlinkSilly:823634273604468787>"

        self.add = "<:add:930273857363927110>"
        self.remove = "<:edit:930273882919821322>"
        self.edit = "<:remove:930273905569042472>"
        self.box = "<:box:987447660510334976>"


class Links:
    def __init__(self):
        self.success = "https://cdn.discordapp.com/emojis/976817167116947507.gif?size=44&quality=lossless"
        self.error = "https://cdn.discordapp.com/emojis/823633973967716363.webp?size=96&quality=lossless"
        self.other = "https://cdn.discordapp.com/emojis/823634273604468787.webp?size=96&quality=lossless"
        self.heart = "https://media.discordapp.net/attachments/947298060646613032/996566385750712400/BloxHeart.png"


class Colors:
    def __init__(self):
        self.success = discord.Colour.from_rgb(67, 181, 130)
        self.error = discord.Colour.from_rgb(240, 74, 71)
        self.warning = discord.Colour.from_rgb(255, 155, 0)
        self.info = discord.Colour.from_rgb(82, 113, 255)
        self.main = discord.Colour.from_rgb(82, 113, 255)


class Releasescolors:
    def __init__(self):
        self.main = discord.Colour.from_rgb(82, 113, 255)
        self.local = discord.Colour.from_rgb(82, 113, 255)


class Badges:
    def __init__(self):
        self.bot = "<:Bot:928765691778203719>"
        self.bughunter = "<:BugHunter:928765827107422268>"
        self.moderator = "<:DiscordCertifiedModerator:881971670921916518>"
        self.staff = "<:DiscordStaff:882405445136965633>"
        self.events = "<:HypeSquadEvents:928765434281488534>"
        self.balance = "<:HypeSquad_Balance:928765104110047273>"
        self.bravery = "<:HypeSquad_Bravery:928765052427841628>"
        self.brilliance = "<:HypeSquad_Brilliance:928764974103404554>"
        self.verifiedbot = "<:VerifiedBot:848277286927073280>"
        self.bughunter2 = "<:BugHunter:928768063933939783>"
        self.partner = "<:DiscordPartner:928768159215923230>"
        self.early = "<:EarlySupporter:928768119072231454>"
        self.botdev = "<:VerfiedBotDeveloper:928765568058785852>"
        self.active_developer = "<:Active_Developer:1086422448804737085>"
        self.old_username = "<:OldUsername:1116488244549398568>"


colors = Colors()
links = Links()
emotes = Emotes()
badges = Badges()
releasescolors = Releasescolors()
