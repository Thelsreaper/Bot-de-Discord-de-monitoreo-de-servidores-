import asyncio
import logging
import os
from pathlib import Path

import discord
from discord.ext import commands
from dotenv import load_dotenv

from core.config import Config
from core.db import DB
from core.monitor import Monitor

load_dotenv()
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s"
)
log = logging.getLogger("gamebot")


class GameBot(commands.Bot):
    def __init__(self):
        super().__init__(
            command_prefix=commands.when_mentioned, intents=discord.Intents.default()
        )
        self.cfg = Config(os.getenv("CONFIG_PATH", "config.yml"))
        self.db = DB(self.cfg.db_path)
        self.monitor = Monitor(self.cfg, self.db)
        self._monitor_task: asyncio.Task | None = None

    async def setup_hook(self):
        await self.db.start()
        await self.monitor.load()
        # Carga automática: todo archivo cogs/*.py (sin guion bajo inicial)
        for path in sorted((Path(__file__).parent / "cogs").glob("[!_]*.py")):
            await self.load_extension(f"cogs.{path.stem}")
            log.info("Cog cargado: %s", path.stem)
        await self.tree.sync()
        self._monitor_task = asyncio.create_task(self.monitor.run())

    async def on_ready(self):
        log.info("Conectado como %s", self.user)

    async def close(self):
        if self._monitor_task:
            self._monitor_task.cancel()
        await self.db.close()
        await super().close()


if __name__ == "__main__":
    GameBot().run(os.environ["DISCORD_TOKEN"])
