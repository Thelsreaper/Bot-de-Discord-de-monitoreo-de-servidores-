import asyncio

from mcstatus import JavaServer

from .base import ServerStatus, register


@register("minecraft")
class MinecraftJava:
    async def fetch(self, cfg: dict, timeout: float) -> ServerStatus:
        server = JavaServer(cfg["host"], cfg["port"], timeout=timeout)
        st = await server.async_status()
        names = [p.name for p in (st.players.sample or [])]

        if cfg.get("query"):  # lista completa (enable-query=true)
            try:
                # mcstatus usa el mismo puerto del objeto para query:
                # si query.port es distinto, se crea otro objeto.
                qserver = JavaServer(
                    cfg["host"], cfg.get("query_port", cfg["port"]), timeout=timeout
                )
                # límite propio: query caído no debe marcar el servidor apagado
                q = await asyncio.wait_for(qserver.async_query(), min(timeout, 3))
                names = list(q.players.list)
            except Exception:
                pass

        return ServerStatus(
            online=True,
            players_online=st.players.online,
            players_max=st.players.max,
            players=names,
            latency_ms=st.latency,
            version=st.version.name,
            motd=st.motd.to_plain(),
        )
