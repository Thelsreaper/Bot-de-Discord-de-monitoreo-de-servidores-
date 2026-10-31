from dataclasses import dataclass, field


@dataclass
class ServerStatus:
    online: bool
    players_online: int = 0
    players_max: int = 0
    players: list[str] = field(default_factory=list)  # nombres (si se conocen)
    players_known: bool = True   # False = proveedor no sabe cuántos hay
    latency_ms: float | None = None
    version: str | None = None
    motd: str | None = None
    extra: dict = field(default_factory=dict)  # ej. {"tps": 19.8}


REGISTRY: dict[str, object] = {}


def register(name: str):
    """Decorador: registra un proveedor con el nombre usado en `type:`."""

    def deco(cls):
        REGISTRY[name] = cls()
        return cls

    return deco


def get_provider(name: str):
    try:
        return REGISTRY[name]
    except KeyError:
        raise ValueError(
            f"Tipo '{name}' desconocido. Disponibles: {', '.join(REGISTRY)}"
        )
