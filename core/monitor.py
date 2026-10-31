import asyncio
import logging
import time
from datetime import date

from providers import ServerStatus, get_provider

log = logging.getLogger("gamebot.monitor")


class Monitor:
    """Consulta todos los servidores en bucle y guarda el último estado.

    Los cogs leen `status` y `online_since`; nunca consultan servidores
    directamente. Así hay una sola consulta por ciclo.
    """

    def __init__(self, cfg, db):
        self.cfg = cfg
        self.db = db
        self.status: dict[str, ServerStatus] = {}
        self.online_since: dict[str, float | None] = {}
        self._last_poll: float = 0.0

    async def load(self):
        self.online_since = await self.db.load_states()

    async def run(self):
        while True:
            try:
                await self.poll_once()
            except Exception:
                log.exception("Error en ciclo de monitoreo")
            await asyncio.sleep(self.cfg.poll_seconds)

    async def _fetch(self, sid: str, srv: dict):
        provider = get_provider(srv.get("type", "a2s"))
        try:
            st = await asyncio.wait_for(
                provider.fetch(srv, self.cfg.timeout), self.cfg.timeout * 2 + 2
            )
        except Exception as exc:
            log.warning("%s fuera de línea: %r", srv["name"], exc)
            st = ServerStatus(online=False)
        return sid, st

    async def poll_once(self):
        now = time.time()
        elapsed = 0.0
        if self._last_poll:
            elapsed = min(now - self._last_poll, self.cfg.poll_seconds * 3)
        self._last_poll = now

        results = await asyncio.gather(
            *(self._fetch(sid, s) for sid, s in self.cfg.servers.items())
        )
        today = date.today().isoformat()
        for sid, st in results:
            self.status[sid] = st
            since = self.online_since.get(sid)
            if st.online and since is None:
                self.online_since[sid] = now
                await self.db.set_online_since(sid, now)
            elif not st.online and since is not None:
                self.online_since[sid] = None
                await self.db.set_online_since(sid, None)
            if st.online and st.players and elapsed:
                await self.db.add_playtime(sid, st.players, int(elapsed), today)
