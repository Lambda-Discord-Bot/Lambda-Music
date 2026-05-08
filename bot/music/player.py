from __future__ import annotations

import asyncio
import logging
from collections.abc import Awaitable, Callable

import discord

from bot.music.models import RepeatMode, Track
from bot.music.queue import MusicQueue
from bot.music.ytdl_source import YTDLSource

logger = logging.getLogger(__name__)


class GuildMusicPlayer:
    def __init__(self, bot: discord.Client, guild: discord.Guild) -> None:
        self.bot = bot
        self.guild = guild
        self.queue = MusicQueue()
        self.current: Track | None = None
        self.repeat_mode = RepeatMode.OFF

        self._voice_client: discord.VoiceClient | None = None
        self._playback_task: asyncio.Task[None] | None = None
        self._track_finished: asyncio.Event | None = None
        self._stopping = False
        self.on_state_change: Callable[[], Awaitable[None]] | None = None

    @property
    def voice_client(self) -> discord.VoiceClient | None:
        if self._voice_client and self._voice_client.is_connected():
            return self._voice_client
        return self.guild.voice_client

    async def connect(self, channel: discord.VoiceChannel) -> discord.VoiceClient:
        voice = self.voice_client
        if voice and voice.channel and voice.channel.id != channel.id:
            await voice.move_to(channel)
            self._voice_client = voice
            return voice

        if voice is None:
            voice = await channel.connect(self_deaf=True)
            self._voice_client = voice
        return voice

    async def ensure_playback_loop(self) -> None:
        if self._playback_task is None or self._playback_task.done():
            self._playback_task = asyncio.create_task(self._playback_loop(), name=f"player-{self.guild.id}")

    async def enqueue(self, query: str, requester: discord.Member | discord.User) -> Track:
        track = await YTDLSource.create_track(query, requester)
        await self.queue.put(track)
        await self.ensure_playback_loop()
        await self._notify_state_change()
        return track

    async def _playback_loop(self) -> None:
        while True:
            track = await self.queue.get()
            self.current = track
            self._track_finished = asyncio.Event()
            await self._notify_state_change()

            voice = self.voice_client
            if voice is None:
                logger.warning("Voice client missing in guild=%s", self.guild.id)
                self.current = None
                continue

            try:
                source = await YTDLSource.create_audio_source(track.webpage_url)
            except Exception as exc:
                logger.exception("Source creation failed: guild=%s track=%s", self.guild.id, track.webpage_url)
                self.current = None
                await self._notify_state_change()
                continue

            def _after_playback(error: Exception | None) -> None:
                if error:
                    logger.error("Playback ended with error in guild=%s: %s", self.guild.id, error)
                if self._track_finished is not None:
                    self.bot.loop.call_soon_threadsafe(self._track_finished.set)

            voice.play(source, after=_after_playback)
            await self._track_finished.wait()

            if self.repeat_mode is RepeatMode.ONE and not self._stopping:
                await self.queue.push_front(track)
            elif self.repeat_mode is RepeatMode.ALL and not self._stopping:
                await self.queue.put(track)

            self._stopping = False
            self.current = None
            await self._notify_state_change()

    async def pause(self) -> bool:
        voice = self.voice_client
        if voice and voice.is_playing():
            voice.pause()
            return True
        return False

    async def resume(self) -> bool:
        voice = self.voice_client
        if voice and voice.is_paused():
            voice.resume()
            return True
        return False

    async def skip(self) -> bool:
        voice = self.voice_client
        if voice and (voice.is_playing() or voice.is_paused()):
            self._stopping = False
            voice.stop()
            return True
        return False

    async def stop(self) -> bool:
        voice = self.voice_client
        await self.queue.clear()
        self._stopping = True

        if voice and (voice.is_playing() or voice.is_paused()):
            voice.stop()
            self.current = None
            await self._notify_state_change()
            return True

        self.current = None
        await self._notify_state_change()
        return False

    async def shuffle(self) -> None:
        await self.queue.shuffle()
        await self._notify_state_change()

    async def leave(self) -> bool:
        voice = self.voice_client
        await self.stop()
        if voice and voice.is_connected():
            await voice.disconnect(force=True)
            self._voice_client = None
            await self._notify_state_change()
            return True
        return False

    async def toggle_repeat(self) -> RepeatMode:
        self.repeat_mode = self.repeat_mode.next_mode()
        await self._notify_state_change()
        return self.repeat_mode

    async def queue_snapshot(self) -> list[Track]:
        return await self.queue.snapshot()

    async def shutdown(self) -> None:
        await self.leave()
        if self._playback_task and not self._playback_task.done():
            self._playback_task.cancel()
            try:
                await self._playback_task
            except asyncio.CancelledError:
                pass

    async def _notify_state_change(self) -> None:
        if self.on_state_change is not None:
            try:
                await self.on_state_change()
            except Exception:
                logger.exception("State-change callback failed in guild=%s", self.guild.id)
