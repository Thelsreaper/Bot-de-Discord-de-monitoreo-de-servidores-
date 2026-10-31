# Gamebot

Bot de Discord. Muestra estado, jugadores, IP y puerto de servidores de juegos.

Soporta Minecraft Java, Minecraft Bedrock, juegos con protocolo Steam
(ARK, Valheim, CS2, etc.) y comprobación TCP simple.

## Comandos

| Comando | Qué hace |
|---|---|
| `/panel crear servidor:<x>` | Mensaje fijo que se edita solo. Requiere Gestionar servidor |
| `/panel quitar` | Borra los paneles del canal |
| `/estado [servidor]` | Estado puntual de uno o todos |
| `/top [servidor] [periodo]` | Jugadores más activos |

## Inicio rápido

1. Crea la aplicación en el Discord Developer Portal.
   debera tener los permisos de /Ver canales / Enviar Mensajes / Insertar enlacens / el valor de los permisos sera de 19456
   Copia el token del bot.
   Scopes de invitación: `bot` y `applications.commands`.

2. Prepara los archivos:
   ```bash
   cp .env.example .env       
     DISCORD_TOKEN=      # pega DISCORD_TOKEN
   chmod 600 .env
   cp config.example.yml config.yml  # edita tus servidores
   mkdir -p data && sudo chown 10001:10001 data
   ```


3. Arranca:
   ```bash
   docker compose up -d --build
   docker compose logs -f
   ```

## Configuración

Todo se define en `config.yml`. Ver comentarios en `config.example.yml`.

- `host`: IP interna que consulta el bot.
- `public_host`: dominio o IP que se muestra en Discord.
- `type`: `minecraft`, `bedrock`, `a2s` o `tcp`.

Para nombres de jugadores en Minecraft Java: `enable-query=true` en
`server.properties` y `query: true` en `config.yml`.

## Estructura

- `config.example.yml`: plantilla de servidores.
- `providers/`: un archivo por tipo de juego.
- `cogs/`: un archivo por función del bot.
- `core/`: configuración, base de datos, monitor, embeds.

## Añadir un juego

Crea `providers/mijuego.py`:

```python
from .base import ServerStatus, register

@register("mijuego")
class MiJuego:
    async def fetch(self, cfg, timeout):
        return ServerStatus(online=True, players_online=3, players_max=20,
                            players=["Ana"], extra={"tps": 19.8})
```

Usa `type: mijuego` en `config.yml`.

## Añadir un comando

Crea `cogs/micomando.py` con `async def setup(bot)`.
Se carga solo al reiniciar. Acceso a `bot.cfg`, `bot.db`, `bot.monitor`.

## Seguridad

- `.env` y `config.yml` están en `.gitignore`. No los subas.
- Si un token se publica, usa **Reset Token** en el Developer Portal.
- El contenedor corre sin root, con sistema de archivos de solo lectura.
