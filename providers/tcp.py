import asyncio
import time

from .base import ServerStatus, register


@register("tcp")
class TcpCheck:
    """Solo comprueba si el puerto TCP responde. Sin jugadores."""

    async def fetch(self, cfg: dict, timeout: float) -> ServerStatus:
        t0 = time.perf_counter()
        _, writer = await asyncio.wait_for(
            asyncio.open_connection(cfg["host"], cfg["port"]), timeout
        )
        latency = (time.perf_counter() - t0) * 1000
        writer.close()
        await writer.wait_closed()
        return ServerStatus(online=True, players_known=False, latency_ms=latency)
