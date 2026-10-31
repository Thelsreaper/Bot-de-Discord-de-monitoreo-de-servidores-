from pathlib import Path

import yaml

REQUIRED = ("id", "name", "host", "port")


class Config:
    def __init__(self, path: str):
        raw = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
        self.timeout = float(raw.get("timeout", 5))
        self.poll_seconds = int(raw.get("poll_seconds", 30))
        self.panel_refresh_seconds = int(raw.get("panel_refresh_seconds", 30))
        self.db_path = raw.get("db_path", "data/gamebot.db")

        self.servers: dict[str, dict] = {}
        for srv in raw["servers"]:
            for key in REQUIRED:
                if key not in srv:
                    raise ValueError(f"Servidor sin campo '{key}': {srv}")
            if srv["id"] in self.servers:
                raise ValueError(f"id repetido: {srv['id']}")
            self.servers[srv["id"]] = srv
