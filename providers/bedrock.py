from mcstatus import BedrockServer

from .base import ServerStatus, register


@register("bedrock")
class MinecraftBedrock:
    async def fetch(self, cfg: dict, timeout: float) -> ServerStatus:
        st = await BedrockServer(cfg["host"], cfg["port"], timeout=timeout).async_status()
        return ServerStatus(
            online=True,
            players_online=st.players.online,
            players_max=st.players.max,
            latency_ms=st.latency,
            version=st.version.name,
            motd=st.motd.to_plain(),
        )
