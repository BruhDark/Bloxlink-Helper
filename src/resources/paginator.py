from discord.ext.pages import Paginator
import discord
from config import emotes, colors

e = emotes.error
ce = colors.error
embed = discord.Embed(
    description=f"{e} This paginator is not for you!", color=ce)


class CustomPaginator(Paginator):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if self.usercheck:
            if self.user != interaction.user:
                await interaction.response.send_message(embed=embed, ephemeral=True)
                return False
            return self.user == interaction.user
        return True
