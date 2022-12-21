import discord
import lavalink
from config import emotes


class SongRemove(discord.ui.Select):
    def __init__(self, options: list):
        super().__init__(placeholder="Select a song to remove...")
        self.options = options

    async def callback(self, interaction: discord.Interaction):
        index = int(self.values[0])

        player: lavalink.DefaultPlayer = interaction.client.lavalink.player_manager.get(
            interaction.guild.id)
        queue = player.queue

        try:
            item = player.queue.pop(index)
            await interaction.response.edit_message(content=f"{emotes.success} Successfully removed `{item.title}`", view=None)

        except:
            await interaction.response.edit_message(content=f"{emotes.error} Something went wrong while removing the song. Try again.", view=None)
