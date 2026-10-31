from datetime import date, timedelta
from typing import Optional

import discord
from discord import app_commands
from discord.ext import commands

from core.util import fmt_duration, server_autocomplete

MEDALS = ["🥇", "🥈", "🥉"]


class RankingCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="top", description="Jugadores más activos")
    @app_commands.describe(servidor="Vacío = todos", periodo="Rango de tiempo")
    @app_commands.autocomplete(servidor=server_autocomplete)
    @app_commands.choices(
        periodo=[
            app_commands.Choice(name="Hoy", value="1"),
            app_commands.Choice(name="7 días", value="7"),
            app_commands.Choice(name="30 días", value="30"),
            app_commands.Choice(name="Total", value="0"),
        ]
    )
    async def top(
        self,
        interaction: discord.Interaction,
        servidor: Optional[str] = None,
        periodo: str = "7",
    ):
        if servidor and servidor not in self.bot.cfg.servers:
            return await interaction.response.send_message("Servidor no existe.", ephemeral=True)

        days = int(periodo)
        since = "0000-00-00" if days == 0 else (date.today() - timedelta(days=days - 1)).isoformat()
        rows = await self.bot.db.top(servidor, since, limit=10)

        label = "Total" if days == 0 else ("Hoy" if days == 1 else f"Últimos {days} días")
        where = self.bot.cfg.servers[servidor]["name"] if servidor else "Todos los servidores"
        embed = discord.Embed(title=f"🏆 Más activos — {where}", color=discord.Color.gold())
        embed.set_footer(text=label)

        if not rows:
            embed.description = (
                "Sin datos aún. El servidor debe exponer nombres "
                "(Minecraft: `query: true`)."
            )
        else:
            lines = []
            for i, (player, secs) in enumerate(rows):
                medal = MEDALS[i] if i < 3 else f"`{i + 1}.`"
                name = discord.utils.escape_markdown(player)
                lines.append(f"{medal} **{name}** — {fmt_duration(secs)}")
            embed.description = "\n".join(lines)
        await interaction.response.send_message(embed=embed)


async def setup(bot):
    await bot.add_cog(RankingCog(bot))
