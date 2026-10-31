from pathlib import Path

import aiosqlite

SCHEMA = """
CREATE TABLE IF NOT EXISTS panels(
    guild_id   INTEGER,
    channel_id INTEGER,
    message_id INTEGER,
    server_id  TEXT,
    PRIMARY KEY (channel_id, message_id)
);
CREATE TABLE IF NOT EXISTS playtime(
    server_id TEXT,
    player    TEXT,
    day       TEXT,
    seconds   INTEGER,
    PRIMARY KEY (server_id, player, day)
);
CREATE TABLE IF NOT EXISTS server_state(
    server_id    TEXT PRIMARY KEY,
    online_since REAL
);
"""


class DB:
    def __init__(self, path: str):
        self.path = path
        self.conn: aiosqlite.Connection | None = None

    async def start(self):
        Path(self.path).parent.mkdir(parents=True, exist_ok=True)
        self.conn = await aiosqlite.connect(self.path)
        await self.conn.executescript(SCHEMA)
        await self.conn.commit()

    async def close(self):
        if self.conn:
            await self.conn.close()

    # --- paneles ---
    async def add_panel(self, guild_id, channel_id, message_id, server_id):
        await self.conn.execute(
            "INSERT OR REPLACE INTO panels VALUES (?,?,?,?)",
            (guild_id, channel_id, message_id, server_id),
        )
        await self.conn.commit()

    async def list_panels(self):
        async with self.conn.execute(
            "SELECT guild_id, channel_id, message_id, server_id FROM panels"
        ) as cur:
            return await cur.fetchall()

    async def remove_panel(self, channel_id, message_id):
        await self.conn.execute(
            "DELETE FROM panels WHERE channel_id=? AND message_id=?",
            (channel_id, message_id),
        )
        await self.conn.commit()

    async def pop_channel_panels(self, channel_id):
        async with self.conn.execute(
            "SELECT message_id FROM panels WHERE channel_id=?", (channel_id,)
        ) as cur:
            ids = [r[0] for r in await cur.fetchall()]
        await self.conn.execute("DELETE FROM panels WHERE channel_id=?", (channel_id,))
        await self.conn.commit()
        return ids

    # --- tiempo de juego ---
    async def add_playtime(self, server_id, players, seconds, day):
        await self.conn.executemany(
            "INSERT INTO playtime(server_id, player, day, seconds) VALUES (?,?,?,?) "
            "ON CONFLICT(server_id, player, day) "
            "DO UPDATE SET seconds = playtime.seconds + excluded.seconds",
            [(server_id, p, day, seconds) for p in players],
        )
        await self.conn.commit()

    async def top(self, server_id, since_day, limit=10):
        query = "SELECT player, SUM(seconds) AS s FROM playtime WHERE day >= ?"
        args: list = [since_day]
        if server_id:
            query += " AND server_id = ?"
            args.append(server_id)
        query += " GROUP BY player ORDER BY s DESC LIMIT ?"
        args.append(limit)
        async with self.conn.execute(query, args) as cur:
            return await cur.fetchall()

    # --- estado (uptime) ---
    async def load_states(self) -> dict:
        async with self.conn.execute(
            "SELECT server_id, online_since FROM server_state"
        ) as cur:
            return {r[0]: r[1] for r in await cur.fetchall()}

    async def set_online_since(self, server_id, value):
        await self.conn.execute(
            "INSERT OR REPLACE INTO server_state VALUES (?,?)", (server_id, value)
        )
        await self.conn.commit()
