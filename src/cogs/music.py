import asyncio
import datetime
import re
import time
from typing import Union

import discord
import lavalink
import spotipy
from discord import slash_command, Option
from discord.ext import commands
from spotipy import SpotifyClientCredentials
import os
import dotenv
from config import colors, emotes

try:
    dotenv.load_dotenv()
except:
    pass

RURL = re.compile(r'https?://(?:www\.)?.+')
sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(client_id=os.getenv(
    "SPOTIFY_CLIENT_ID"), client_secret=os.getenv("SPOTIFY_CLIENT_SECRET")))


def create_embed(guild: discord.Guild, track: lavalink.AudioTrack, position):
    pos = datetime.timedelta(seconds=position / 1000)
    dur = datetime.timedelta(seconds=int(track.duration / 1000))
    duration = dur - pos
    en = datetime.datetime.now() + duration
    endsat = round(en.timestamp())

    requester: discord.Member = guild.get_member(track.requester)
    embed = discord.Embed(
        title=f"<a:music:1005254786486124625> Currently Playing", description=f"**{track.title}** by {track.author}", color=colors.main)
    embed.add_field(name="Ends", value=f"<t:{endsat}:R>", inline=True)
    embed.add_field(name="Video URL",
                    value=f"[Click here]({track.uri})", inline=False)

    embed.set_footer(
        text=f"Requested by {requester}", icon_url=requester.display_avatar.url)
    return embed


def confirmation(message):
    embed = discord.Embed(
        description=f"{emotes.success} {message}", color=colors.success)
    return embed


async def cleanup(player):
    player.queue.clear()
    await player.stop()


class Player(discord.VoiceClient):

    def __init__(self, client: discord.Client, channel: Union[discord.VoiceChannel, discord.StageChannel]):
        super().__init__(client, channel)
        self.client = client
        self.channel = channel
        if hasattr(self.client, 'lavalink'):
            self.lavalink = self.client.lavalink

    async def on_voice_server_update(self, data):
        lavalink_data = {'t': 'VOICE_SERVER_UPDATE', 'd': data}
        await self.lavalink.voice_update_handler(lavalink_data)

    async def on_voice_state_update(self, data):
        lavalink_data = {'t': 'VOICE_STATE_UPDATE', 'd': data}
        await self.lavalink.voice_update_handler(lavalink_data)

    async def connect(self, *, timeout: float, reconnect: bool, self_deaf: bool = False,
                      self_mute: bool = False) -> None:
        self.lavalink.player_manager.create(guild_id=self.channel.guild.id)
        await self.channel.guild.change_voice_state(channel=self.channel, self_mute=self_mute, self_deaf=self_deaf)

    async def disconnect(self, *, force: bool = False) -> None:
        player = self.lavalink.player_manager.get(self.channel.guild.id)
        if not force and not player.is_connected:
            return
        await self.channel.guild.change_voice_state(channel=None)
        player.channel_id = None
        self.cleanup()


class SongSelect(discord.ui.Select):
    def __init__(self, client, tracks, requester):
        self.client = client
        self.tracks = tracks
        self.requester = requester
        self.keys = {}
        self.success = False

        options = []
        for track in self.tracks:
            options.append(discord.SelectOption(
                label=f"{track.title}", description=f"By {track.author}", emoji="<:playlist:1005265606821548163>"))
            self.keys[f'{track.title}'] = track
        super().__init__(placeholder="Pick a song",
                         min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        if interaction.user != self.requester:
            return await interaction.response.send_message("Invalid user!", ephemeral=True)
        selection = self.values[0]
        song = self.keys[f"{selection}"]
        info = song['info']

        if len(self.client.active_players) == 0:
            await interaction.response.edit_message(embed=confirmation(f"Added {info['title']} to the queue!"), view=None)
        else:
            await interaction.response.edit_message(embed=confirmation(f"Added {info['title']} to the queue!"), view=None)

        player = self.client.lavalink.player_manager.get(interaction.guild.id)
        player.add(track=song, requester=self.requester.id)

        if not player.is_playing:
            await player.play()

        if len(self.client.active_players) == 0:
            bview = Buttons(self.client, interaction)
            embed = create_embed(
                guild=interaction.guild, track=player.current, position=player.position)
            mplayer: discord.WebhookMessage = await interaction.followup.send(embed=embed, view=bview)
            bview.message = mplayer.id
            self.client.active_players.append(mplayer.id)
        self.disabled = True


class Queue(discord.ui.View):

    def __init__(self, client, queue, length):
        super().__init__()
        self.client = client
        self.queue = queue
        self.length = length
        self.position = 0
        self.max = len(queue[::10]) - 1

    def build_queue(self):
        page = 10 * self.position
        songlist = []
        count = 1
        for song in self.queue[page:page + 10]:
            songlist.append(f"**{count + page}:** `{song}`")
            count += 1
        embed = discord.Embed(title="<:queue:1005256368112029696> Upcoming Songs", description=f"\n".join(
            songlist), color=discord.Color.blurple())
        embed.set_footer(
            text=f"{(10 * self.position - 1) + count} of {len(self.queue)} songs - {self.length}")
        return embed

    @discord.ui.button(label="<", style=discord.ButtonStyle.blurple)
    async def queue_prev(self, button: discord.ui.Button, interaction: discord.Interaction):
        self.position -= 1
        if self.position == 0:
            button.disabled = True
        if self.children[1].disabled:
            self.children[1].disabled = False
        embed = self.build_queue()
        await interaction.response.edit_message(embed=embed, view=self)

    @discord.ui.button(label=">", style=discord.ButtonStyle.blurple)
    async def queue_next(self, button: discord.ui.Button, interaction: discord.Interaction):
        self.position += 1
        if self.position == self.max:
            button.disabled = True
        if self.children[0].disabled:
            self.children[0].disabled = False
        embed = self.build_queue()
        await interaction.response.edit_message(embed=embed, view=self)


class Buttons(discord.ui.View):

    def __init__(self, client, interaction):
        super().__init__(timeout=120)
        self.client = client
        self.check_buttons(interaction)

    async def on_timeout(self) -> None:
        self.disable_all_items()
        embed = self.message.embeds[0]
        embed.set_author(name="Timed out. This player won't update anymore.")
        await self.message.edit(view=self)

    def controller(self, interaction):
        player = self.client.lavalink.player_manager.get(interaction.guild.id)
        return player

    def check_buttons(self, interaction):
        player = self.client.lavalink.player_manager.get(interaction.guild.id)
        if player.paused:
            self.children[1].disabled = True
        else:
            self.children[0].disabled = True

    @staticmethod
    def compilequeue(queue):
        titles = []
        lengths = []
        for song in queue:
            titles.append(song.title)
            lengths.append(int(song.duration / 1000))
        return titles, lengths

    @discord.ui.button(emoji="<:play:1005256629064827003>", label="Play", style=discord.ButtonStyle.gray, row=1)
    async def button_play(self, button: discord.ui.Button, interaction: discord.Interaction):
        player = self.controller(interaction)
        embed = create_embed(guild=interaction.guild,
                             track=player.current, position=player.position)
        if player.paused:
            await player.set_pause(pause=False)
            self.children[1].disabled = False
            button.disabled = True
            await interaction.response.edit_message(embed=embed, view=self)
            await interaction.followup.send(f"{emotes.bloxlink} {interaction.user.mention} resumed the player!", allowed_mentions=discord.AllowedMentions(users=False))

    @discord.ui.button(emoji="<:pause:1005256663000961205>", label="Pause", style=discord.ButtonStyle.gray, row=1)
    async def button_pause(self, button: discord.ui.Button, interaction: discord.Interaction):
        player = self.controller(interaction)
        embed = create_embed(guild=interaction.guild,
                             track=player.current, position=player.position)
        if not player.paused:
            await player.set_pause(pause=True)
            self.children[0].disabled = False
            button.disabled = True
            await interaction.response.edit_message(embed=embed, view=self)
            await interaction.followup.send(f"{emotes.bloxlink} {interaction.user.mention} paused the player!", allowed_mentions=discord.AllowedMentions(users=False))

    @discord.ui.button(emoji="<:skip:1005260620989481021>", label="Skip", style=discord.ButtonStyle.gray, row=1)
    async def button_forward(self, button: discord.ui.Button, interaction: discord.Interaction):
        player = self.controller(interaction)
        await player.skip()
        await interaction.response.edit_message(view=self)
        await interaction.followup.send(f"{emotes.bloxlink} {interaction.user.mention} skipped the song!", allowed_mentions=discord.AllowedMentions(users=False))

    @discord.ui.button(emoji="<:stop:1005261869113675800>", label="Stop", style=discord.ButtonStyle.gray, row=1)
    async def button_stop(self, button: discord.ui.Button, interaction: discord.Interaction):
        player = self.controller(interaction)
        embed = discord.Embed(title=f"Stopping player...",
                              color=discord.Color.red())
        voice = interaction.guild.voice_client
        await interaction.response.edit_message(embed=embed, view=None)
        await interaction.followup.send(f"{emotes.bloxlink} {interaction.user.mention} stopped the player!", allowed_mentions=discord.AllowedMentions(users=False))
        if voice:
            await voice.disconnect(force=True)
        await cleanup(player)

    @discord.ui.button(emoji="<:shuffle:1005261849199128576>", label="Shuffle", style=discord.ButtonStyle.gray, row=2)
    async def button_shuffle(self, button: discord.ui.Button, interaction: discord.Interaction):
        player = self.controller(interaction)
        embed = create_embed(guild=interaction.guild,
                             track=player.current, position=player.position)
        await interaction.response.edit_message(embed=embed, view=self)
        if not player.shuffle:
            player.set_shuffle(shuffle=True)
            await interaction.followup.send(f"{emotes.success} Shuffling the queue!")
        else:
            player.set_shuffle(shuffle=False)
            await interaction.followup.send(f"{emotes.success} No longer shuffling the queue!")

    @discord.ui.button(emoji="<:repeat:1005256716050518216>", label="Repeat", style=discord.ButtonStyle.gray, row=2)
    async def button_loop(self, button: discord.ui.Button, interaction: discord.Interaction):
        player = self.controller(interaction)
        embed = create_embed(guild=interaction.guild,
                             track=player.current, position=player.position)
        await interaction.response.edit_message(embed=embed, view=self)
        if not player.repeat:
            player.set_repeat(repeat=True)
            await interaction.channel.send(f"{emotes.success} Looping the queue!")
        else:
            player.set_repeat(repeat=False)
            await interaction.channel.send(f"{emotes.success} No longer looping the queue!")

    @discord.ui.button(emoji="<:queue:1005256368112029696>", label="Queue", style=discord.ButtonStyle.gray, row=2)
    async def button_queue(self, button: discord.ui.Button, interaction: discord.Interaction):
        player = self.controller(interaction)
        queue, length = self.compilequeue(player.queue)
        songlist = []
        for idx, song in enumerate(queue[:10]):
            songlist.append(f"**{idx + 1}:** `{song}`")
        totallength = time.strftime(
            '%H hours, %M minutes, %S seconds', time.gmtime(sum(length)))
        embed = discord.Embed(title="Upcoming Songs", description=f"\n".join(songlist),
                              color=discord.Color.light_gray())
        embed.set_footer(text=f"10 of {len(queue)} songs - {totallength}")
        view = Queue(self.client, queue, totallength)
        ex = view.children[1:] if len(queue) > 10 else view.children[1:2]
        view.disable_all_items(exclusions=ex)
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)


class Music(commands.Cog):

    def __init__(self, client):
        self.client = client
        self.client.lavalink = None
        self.client.active_players = []
        client.loop.create_task(self.connect_nodes())

    async def connect_nodes(self):
        await self.client.wait_until_ready()
        lavaclient = lavalink.Client(self.client.user.id)
        lavaclient.add_node('bh-lavalink.herokuapp.com', 80,
                            'youshallnotpass', 'us', 'music-node')
        lavaclient.add_event_hooks(self)
        self.client.lavalink = lavaclient

    @lavalink.listener(lavalink.events.QueueEndEvent)
    async def queue_ending(self, event: lavalink.QueueEndEvent):
        guild_id = event.player.guild_id
        guild = self.client.get_guild(guild_id)
        await guild.voice_client.disconnect(force=True)

    @lavalink.listener(lavalink.events.TrackStartEvent)
    async def track_started(self, event: lavalink.TrackStartEvent):
        players = self.client.active_players
        for player in players:
            message: discord.Message = self.client.get_message(player)
            await message.edit(embed=create_embed(guild=message.guild, track=event.track, position=event.track.position))

    @lavalink.listener(lavalink.events.TrackStuckEvent)
    async def track_stuck(self, event: lavalink.TrackStuckEvent):
        await event.player.skip()

    @staticmethod
    def is_privileged(user, track):
        return True

    @staticmethod
    def get_spotify_tracks(query):  # spotify you suck this took so long to figure out
        songlist = []
        match re.findall(r'/track/|/album/|/playlist/', query)[0]:
            case '/track/':
                track = sp.track(query)
                songlist.append(
                    f"{track['album']['artists'][0]['name']} - {track['name']}")
            case '/album/':
                tracks = sp.album(query)
                for track in tracks['tracks']['items']:
                    songlist.append(
                        f"{track['artists'][0]['name']} - {track['name']}")
            case '/playlist/':
                tracks = sp.playlist(query)
                for track in tracks['tracks']['items']:
                    actualtrack = track['track']  # why
                    songlist.append(
                        f"{actualtrack['album']['artists'][0]['name']} - {actualtrack['name']}")
            case _:
                pass
        return songlist

    @commands.Cog.listener()
    async def on_voice_state_update(self, member: discord.Member, before: discord.VoiceState,
                                    after: discord.VoiceState):
        voice = discord.utils.get(
            self.client.voice_clients, guild=member.guild)
        player = self.client.lavalink.player_manager.get(member.guild.id)
        if not voice:
            if player:
                await cleanup(player)
            return
        elif voice.channel != before.channel:  # ignore if the member joined a voice channel
            return
        elif member.bot:
            return
        if after.channel != before.channel:
            memberlist = []
            for m in before.channel.members:
                if m.bot:
                    continue
                memberlist.append(m)
            if not memberlist:
                if player.is_playing:
                    await cleanup(player)
                await voice.disconnect(force=True)

    @slash_command(description="Play some music")
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def music(self, ctx: discord.ApplicationContext, search: Option(str, description="Music query or URL", required=False, default=None)):
        try:
            channel = ctx.author.voice.channel
        except AttributeError:
            return await ctx.respond(f"{emotes.error} You need to be in a voice channel!", ephemeral=True)
        player = self.client.lavalink.player_manager.create(ctx.guild.id)
        try:
            await channel.connect(cls=Player)
        except discord.ClientException:
            await ctx.guild.voice_client.move_to(channel)
        if search:
            if len(search) > 256:
                return await ctx.respond(f"{emotes.error} Search query has a maximum of 256 characters!", ephemeral=True)
            elif player.is_playing:
                if len(player.queue) >= 250:
                    return await ctx.respond(f"{emotes.error} The queue is full!", ephemeral=True)
            search = f'ytsearch:{search}' if not RURL.match(search) else search
            results = await player.node.get_tracks(search)
            tracks = results.tracks
            total = len(player.queue)
            match results.load_type:
                case lavalink.LoadType.PLAYLIST:
                    await ctx.defer()
                    count = 0
                    for track in tracks:
                        if total + count < 250:
                            player.add(track=track, requester=ctx.author.id)
                            count += 1

                    if len(self.client.active_players) == 0:
                        await ctx.interaction.followup.send(embed=confirmation(f"Added {count} songs to the queue"))
                        bview = Buttons(self.client, ctx.interaction)
                        if not self.is_privileged(ctx.author, player.current):
                            bview.disable_all_items()
                            bview.children[5].disabled = False
                            embed = create_embed(
                                guild=ctx.guild, track=player.current, position=player.position)
                            mplayer = await ctx.interaction.followup.send(embed=embed, view=bview)
                            bview.message = mplayer.id
                            self.client.active_players.append(mplayer.id)

                    else:
                        await ctx.respond(embed=confirmation(f"Added {count} songs to the queue"), ephemeral=True)

                    if not player.is_playing:
                        await player.play()
                case lavalink.LoadType.TRACK:
                    song = tracks[0]
                    if len(self.client.active_players) != 0:
                        await ctx.respond(embed=confirmation(f"Adding {song.title} to the queue"))
                        bview = Buttons(self.client, ctx.interaction)
                        if not self.is_privileged(ctx.author, player.current):
                            bview.disable_all_items()
                            bview.children[5].disabled = False
                            embed = create_embed(
                                guild=ctx.guild, track=player.current, position=player.position)
                            mplayer = await ctx.interaction.followup.send(embed=embed, view=bview)
                            bview.message = mplayer.id
                            self.client.active_players.append(mplayer.id)
                    else:
                        await ctx.respond(embed=confirmation(f"Adding {song.title} to the queue"), ephemeral=True)

                    player.add(track=song, requester=ctx.author.id)
                    if not player.is_playing:
                        await player.play()
                case lavalink.LoadType.SEARCH:
                    view = discord.ui.View(timeout=30)
                    view.add_item(SongSelect(
                        self.client, tracks[:5], ctx.author))

                    if len(self.client.active_players) != 0:
                        message = await ctx.respond(view=view, ephemeral=True)

                    else:
                        message = await ctx.respond(view=view)
                    await view.wait()

                    if not view.children[0].disabled:  # returns True if a song wasn't picked
                        
                        await message.edit_original_message(content=f"{emotes.error} No song selected! Prompt cancelled.", view=None)
                case _:
                    if 'open.spotify.com' or 'spotify:' in search:
                        await ctx.defer()
                        spotifysongs = self.get_spotify_tracks(query=search)
                        if not spotifysongs:
                            return await ctx.respond("Couldn't find any music!", ephemeral=True)
                        s_results = await asyncio.wait_for(asyncio.gather(*[player.node.get_tracks(
                            f'ytsearch:{song}') for song in spotifysongs]), timeout=30)
                        count = 0
                        for track in s_results:
                            if total + count < 250:
                                player.add(
                                    track=track.tracks[0], requester=ctx.author.id)
                                count += 1
                        if len(self.client.active_players) == 0:
                            await ctx.respond(embed=confirmation(f"Added {count} spotify song(s) to the queue"))
                            bview = Buttons(self.client, ctx.interaction)
                            if not self.is_privileged(ctx.author, player.current):
                                bview.disable_all_items()
                                bview.children[5].disabled = False
                                embed = create_embed(
                                    guild=ctx.guild, track=player.current, position=player.position)
                                mplayer = await ctx.interaction.followup.send(embed=embed, view=bview)
                                bview.message = mplayer.id
                                self.client.active_players.append(
                                    mplayer.id)

                        else:
                            await ctx.respond(embed=confirmation(f"Added {count} spotify song(s) to the queue"), ephemeral=True)

                        if not player.is_playing:
                            await player.play()
                    else:
                        return await ctx.respond(f"{emotes.error} Couldn't find any music!", ephemeral=True)
        else:
            if not player.is_playing:
                return await ctx.respond(f"{emotes.error} No music playing!", ephemeral=True)
            bview = Buttons(self.client, ctx.interaction)
            if not self.is_privileged(ctx.author, player.current):
                bview.disable_all_items()
                bview.children[5].disabled = False
            embed = create_embed(
                guild=ctx.guild, track=player.current, position=player.position)
            mplayer = await ctx.respond(embed=embed, view=bview)
            bview.message = await mplayer.original_message()
            self.client.active_players.append(bview.message.id)


def setup(bot):
    bot.add_cog(Music(bot))
