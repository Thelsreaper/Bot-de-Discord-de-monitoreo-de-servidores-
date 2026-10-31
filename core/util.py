from discord import app_commands


def fmt_duration(seconds: float) -> str:
    seconds = int(seconds)
    d, rem = divmod(seconds, 86400)
    h, rem = divmod(rem, 3600)
    m, _ = divmod(rem, 60)
    parts = []
    if d:
        parts.append(f"{d}d")
    if h:
        parts.append(f"{h}h")
    if m or not parts:
        parts.append(f"{m}m")
    return " ".join(parts)


async def server_autocomplete(interaction, current: str):
    """Autocompletado de servidores definidos en config.yml."""
    cur = current.lower()
    servers = interaction.client.cfg.servers
    return [
        app_commands.Choice(name=s["name"][:100], value=sid)
        for sid, s in servers.items()
        if cur in s["name"].lower() or cur in sid.lower()
    ][:25]
