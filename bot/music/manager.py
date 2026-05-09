from __future__ import annotations

import logging

import discord

from bot.music.player import GuildMusicPlayer

logger = logging.getLogger(__name__)


class MusicManager:
    def __init__(self, bot: discord.Client) -> None:
        self.bot = bot
        self._players: dict[int, GuildMusicPlayer] = {}
        self._panel_messages: dict[int, set[tuple[int, int]]] = {}
        self._latest_refresh_version: dict[int, int] = {}

    def get_player(self, guild: discord.Guild) -> GuildMusicPlayer:
        player = self._players.get(guild.id)
        if player is None:
            player = GuildMusicPlayer(self.bot, guild)
            player.on_state_change = lambda version: self.refresh_panels(guild.id, version)
            self._players[guild.id] = player
        return player

    def register_panel_message(self, guild_id: int, channel_id: int, message_id: int) -> None:
        refs = self._panel_messages.setdefault(guild_id, set())
        refs.add((channel_id, message_id))

    async def refresh_panels(self, guild_id: int, version: int | None = None) -> None:
        refs = self._panel_messages.get(guild_id)
        if not refs:
            return

        guild = self.bot.get_guild(guild_id)
        if guild is None:
            return

        if version is not None:
            latest = self._latest_refresh_version.get(guild_id, 0)
            if version < latest:
                return
            self._latest_refresh_version[guild_id] = version

        from bot.ui.embeds import build_panel_embed
        from bot.ui.panel import MusicPanelView

        player = self.get_player(guild)
        embed = build_panel_embed(player)
        stale_refs: set[tuple[int, int]] = set()

        for channel_id, message_id in refs:
            if version is not None and version < self._latest_refresh_version.get(guild_id, version):
                return

            channel = self.bot.get_channel(channel_id)
            if channel is None:
                try:
                    fetched = await self.bot.fetch_channel(channel_id)
                    channel = fetched if isinstance(fetched, discord.TextChannel) else None
                except (discord.NotFound, discord.Forbidden, discord.HTTPException):
                    channel = None

            if channel is None or not isinstance(channel, discord.TextChannel):
                stale_refs.add((channel_id, message_id))
                continue

            try:
                panel_message = channel.get_partial_message(message_id)
                await panel_message.edit(embed=embed, view=MusicPanelView(self))
            except (discord.NotFound, discord.Forbidden):
                stale_refs.add((channel_id, message_id))
            except discord.HTTPException as exc:
                logger.warning("Failed to refresh panel message %s in guild=%s: %s", message_id, guild_id, exc)
            except Exception as exc:
                logger.exception("Unexpected panel refresh error in guild=%s message=%s: %s", guild_id, message_id, exc)

        for ref in stale_refs:
            refs.discard(ref)

    async def shutdown(self) -> None:
        for player in self._players.values():
            await player.shutdown()
        self._players.clear()
        self._panel_messages.clear()
        self._latest_refresh_version.clear()
