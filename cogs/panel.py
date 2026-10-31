import logging

import discord
from discord import app_commands
from discord.ext import commands, tasks

from core.embeds import server_embed, status_embed
from core.util import server_autocomplete

log = logging.getLogger("gamebot.panel")


class PanelCog(commands.Cog):
    """Mensajes fijos que se editan solos con el estado del servidor."""

    panel = app_commands.Group(
        name="panel",
        description="Paneles de estado en vivo",
        guild_only=True,
        default_permissions=discord.Permissions(manage_guild=True),
    )

    def __init__(self, bot):
        self.bot = bot

    async def cog_load(self):
        self.refresh.change_interval(seconds=self.bot.cfg.panel_refresh_seconds)
        self.refresh.start()

    async def cog_unload(self):
        self.refresh.cancel()

    @panel.command(name="crear", description="Crea panel en este canal")
    @app_commands.describe(servidor="Servidor a mostrar")
    @app_commands.autocomplete(servidor=server_autocomplete)
    async def crear(self, interaction: discord.Interaction, servidor: str):
        srv = self.bot.cfg.servers.get(servidor)
        if not srv:
            return await interaction.response.send_message("Servidor no existe.", ephemeral=True)
        await interaction.response.defer(ephemeral=True)
        try:
            msg = await interaction.channel.send(embed=server_embed(self.bot, servidor))
        except discord.Forbidden:
            return await interaction.followup.send("Sin permiso para escribir aquí.")
        await self.bot.db.add_panel(interaction.guild_id, interaction.channel_id, msg.id, servidor)
        await interaction.followup.send(f"Panel de **{srv['name']}** creado.")

    @panel.command(name="quitar", description="Quita paneles de este canal")
    async def quitar(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        ids = await self.bot.db.pop_channel_panels(interaction.channel_id)
        for mid in ids:
            try:
                await interaction.channel.get_partial_message(mid).delete()
            except discord.HTTPException:
                pass
        await interaction.followup.send(f"Paneles quitados: {len(ids)}.")

    @tasks.loop(seconds=30)
    async def refresh(self):
        for _, channel_id, message_id, server_id in await self.bot.db.list_panels():
            if server_id not in self.bot.cfg.servers:
                continue
            try:
                channel = self.bot.get_channel(channel_id) or await self.bot.fetch_channel(channel_id)
                await channel.get_partial_message(message_id).edit(
                    embed=server_embed(self.bot, server_id)
                )
            except discord.NotFound:
                await self.bot.db.remove_panel(channel_id, message_id)
            except Exception as exc:
                log.warning("Panel %s/%s: %s", channel_id, message_id, exc)

    @refresh.before_loop
    async def _before(self):
        await self.bot.wait_until_ready()


async def setup(bot):
    await bot.add_cog(PanelCog(bot))
