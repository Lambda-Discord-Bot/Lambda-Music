from __future__ import annotations

import logging

import discord
from discord.ext import commands

from bot.core.settings import Settings
from bot.music.manager import MusicManager
from bot.ui.panel import MusicPanelView

logger = logging.getLogger(__name__)


class LambdaMusicBot(commands.Bot):
    def __init__(self, settings: Settings) -> None:
        intents = discord.Intents.default()
        intents.guilds = True
        intents.voice_states = True

        super().__init__(command_prefix="!", intents=intents)
        self.settings = settings
        self.music_manager = MusicManager(self)
        self._synced_once = False

    async def setup_hook(self) -> None:
        await self.load_extension("bot.cogs.music_panel")
        self.add_view(MusicPanelView(self.music_manager))

    async def on_ready(self) -> None:
        if not self._synced_once:
            synced = await self.tree.sync()
            logger.info("Slash commands synced: %s", len(synced))
            self._synced_once = True

        logger.info("Logged in as %s (%s)", self.user, self.user.id if self.user else "?")

    async def close(self) -> None:
        await self.music_manager.shutdown()
        await super().close()
