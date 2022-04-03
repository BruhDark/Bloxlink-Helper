import discord

PREFIX = "o!"
DESCRIPTION = "Bloxlink HQ's tags bot."

EMOTES = {
    "success": "<:BloxlinkHappy:823633735446167552>",
    "error": "<:BloxlinkDead:823633973967716363>",

    "warning": ":warning:",
    "info": "<:info:881973831974154250>",
    "question": "<:Question:929051955962195999>",

    "operational": "<:Operational:882404710148083724>",
    "partialoutage": "<:PartialOutage:882404755949895730>",
    "majoroutage": "<:MajorOutage:882404641286000681>",
    "maintenance": "<:UnderMaintenance:881969909247148052>",

    "dnd": "<:DoNotDisturb:928716110822518834>",
    "idle": "<:Idle:929049988573581352>",
    "online": "<:Online:928716318054694993>",
    "offline": "<:Offline:928716879474851870>",

    "loading": "<a:loading:946809583194767400>",
    "spotify": "<:Spotify:929060525881565224>",
    "943150072827355177": "<:BloxlinkSilly:823634273604468787>",
 
    "add": "<:add:930273857363927110>",
    "remove": "<:edit:930273882919821322>",
    "edit": "<:remove:930273905569042472>",
}

LINKS = {
    "success": "https://cdn.discordapp.com/emojis/823633735446167552.webp?size=96&quality=lossless",
    "error": "https://cdn.discordapp.com/emojis/823633973967716363.webp?size=96&quality=lossless",
    "other": "https://cdn.discordapp.com/emojis/823634273604468787.webp?size=96&quality=lossless"
}

COLORS = {
    "success": discord.Colour.from_rgb(67, 181, 130),
    "error": discord.Colour.from_rgb(240, 74, 71),
    "warning": discord.Colour.from_rgb(255, 155, 0),
    "info": discord.Colour.from_rgb(113, 134, 213),
    }

RELEASESCOLORS = {
    "943150072827355177": discord.Colour.from_rgb(58, 61, 255)
}

AUTHORIZED = [449245847767482379]

BADGES = {
    "bot": "<:Bot:928765691778203719>",
    "bughunter": "<:BugHunter:928765827107422268>",
    "moderator": "<:DiscordCertifiedModerator:881971670921916518>",
    "staff": "<:DiscordStaff:882405445136965633>",
    "events": "<:HypeSquadEvents:928765434281488534>",
    "balance": "<:HypeSquad_Balance:928765104110047273>",
    "bravery": "<:HypeSquad_Bravery:928765052427841628>",
    "brilliance": "<:HypeSquad_Brilliance:928764974103404554>",
    "verifiedbot": "<:VerifiedBot:848277286927073280>",
    "bughunter2": "<:BugHunter:928768063933939783>",
    "partner": "<:DiscordPartner:928768159215923230>",
    "early": "<:EarlySupporter:928768119072231454>",
    "botdev": "<:VerfiedBotDeveloper:928765568058785852>"
}