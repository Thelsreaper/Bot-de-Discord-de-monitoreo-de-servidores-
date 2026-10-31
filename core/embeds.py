import discord

from .util import fmt_duration


def _address(srv: dict) -> str:
    return f"{srv.get('public_host', srv['host'])}:{srv['port']}"


def status_embed(srv: dict, st, online_since) -> discord.Embed:
    if st is None:
        return discord.Embed(
            title=srv["name"],
            description="Consultando…",
            color=discord.Color.light_grey(),
        )

    embed = discord.Embed(
        title=srv["name"],
        color=discord.Color.green() if st.online else discord.Color.red(),
    )
    if st.online:
        embed.add_field(name="🟢 Estado", value="Activo")
    else:
        embed.add_field(name="🔴 Estado", value="Apagado")
    embed.add_field(name="🌐 Dirección", value=f"`{_address(srv)}`")

    if st.online:
        if st.players_known:
            embed.add_field(
                name="👥 Jugadores", value=f"{st.players_online} / {st.players_max}"
            )
        if st.extra.get("tps") is not None:
            embed.add_field(name="📊 TPS", value=f"{st.extra['tps']:.2f}")
        if st.latency_ms is not None:
            embed.add_field(name="📶 Ping", value=f"{st.latency_ms:.0f} ms")
        if online_since:
            import time

            embed.add_field(
                name="⏱️ Tiempo activo",
                value=fmt_duration(time.time() - online_since),
            )
        if st.version:
            embed.add_field(name="📡 Versión", value=str(st.version)[:100])
        if st.motd:
            embed.add_field(name="📝 MOTD", value=st.motd[:1000], inline=False)
        if st.players:
            names = ", ".join(sorted(st.players, key=str.lower))
            embed.add_field(
                name="🧑 Conectados",
                value=discord.utils.escape_markdown(names)[:1000],
                inline=False,
            )

    embed.set_footer(text="Actualizado")
    embed.timestamp = discord.utils.utcnow()
    return embed


def server_embed(bot, sid: str) -> discord.Embed:
    return status_embed(
        bot.cfg.servers[sid],
        bot.monitor.status.get(sid),
        bot.monitor.online_since.get(sid),
    )


def overview_embed(bot) -> discord.Embed:
    lines, total = [], 0
    for sid, srv in bot.cfg.servers.items():
        st = bot.monitor.status.get(sid)
        if st is None:
            lines.append(f"⚪ **{srv['name']}** — consultando…")
        elif st.online:
            if st.players_known:
                total += st.players_online
                info = f"{st.players_online}/{st.players_max}"
            else:
                info = "activo"
            lines.append(f"🟢 **{srv['name']}** — {info} · `{_address(srv)}`")
        else:
            lines.append(f"🔴 **{srv['name']}** — apagado · `{_address(srv)}`")
    embed = discord.Embed(
        title="Servidores de juegos",
        description="\n".join(lines) + f"\n\nJugadores totales: **{total}**",
        color=discord.Color.blurple(),
    )
    embed.timestamp = discord.utils.utcnow()
    return embed
