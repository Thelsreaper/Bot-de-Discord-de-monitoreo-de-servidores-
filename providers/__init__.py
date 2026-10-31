import importlib
import pkgutil

from .base import ServerStatus, get_provider, register

__all__ = ["ServerStatus", "get_provider", "register"]

# Importa todo módulo de esta carpeta: soltar un archivo = nuevo tipo de juego.
for _mod in pkgutil.iter_modules(__path__):
    if _mod.name != "base":
        importlib.import_module(f"{__name__}.{_mod.name}")
