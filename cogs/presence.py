import discord
from discord.ext import commands, tasks


class PresenceCog(commands.Cog):
    """Estado del bot: 'Viendo N jugadores'."""

    def __init__(self, bot):
        self.bot = bot

    async def cog_load(self):
        self.update.start()

    async def cog_unload(self):
        self.update.cancel()

    @tasks.loop(seconds=60)
    async def update(self):
        total = sum(
            s.players_online
            for s in self.bot.monitor.status.values()
            if s.online and s.players_known
        )
        await self.bot.change_presence(
            activity=discord.Activity(
                type=discord.ActivityType.watching, name=f"{total} jugadores"
            )
        )

    @update.before_loop
    async def _before(self):
        await self.bot.wait_until_ready()


async def setup(bot):
    await bot.add_cog(PresenceCog(bot))
