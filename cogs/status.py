from typing import Optional

import discord
from discord import app_commands
from discord.ext import commands

from core.embeds import overview_embed, server_embed
from core.util import server_autocomplete


class StatusCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="estado", description="Estado de uno o todos los servidores")
    @app_commands.describe(servidor="Vacío = todos")
    @app_commands.autocomplete(servidor=server_autocomplete)
    async def estado(self, interaction: discord.Interaction, servidor: Optional[str] = None):
        if servidor is None:
            await interaction.response.send_message(embed=overview_embed(self.bot))
        elif servidor in self.bot.cfg.servers:
            await interaction.response.send_message(embed=server_embed(self.bot, servidor))
        else:
            await interaction.response.send_message("Servidor no existe.", ephemeral=True)


async def setup(bot):
    await bot.add_cog(StatusCog(bot))
