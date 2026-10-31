import a2s

from .base import ServerStatus, register


@register("a2s")
class SourceQuery:
    """Protocolo Steam Query: ARK, Rust, Valheim, CS2, etc."""

    async def fetch(self, cfg: dict, timeout: float) -> ServerStatus:
        addr = (cfg["host"], cfg.get("query_port", cfg["port"]))
        info = await a2s.ainfo(addr, timeout=timeout)
        names: list[str] = []
        try:
            players = await a2s.aplayers(addr, timeout=timeout)
            names = [p.name for p in players if p.name]
        except Exception:
            pass
        return ServerStatus(
            online=True,
            players_online=info.player_count,
            players_max=info.max_players,
            players=names,
            latency_ms=info.ping * 1000,
            version=info.version,
            motd=info.server_name,
        )
