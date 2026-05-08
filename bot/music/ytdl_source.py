from __future__ import annotations

import asyncio
from concurrent.futures import ThreadPoolExecutor
from typing import Any

import discord
import yt_dlp

from bot.music.models import Track


_YTDL_OPTIONS: dict[str, Any] = {
    "format": "bestaudio/best",
    "noplaylist": True,
    "default_search": "ytsearch",
    "quiet": True,
    "no_warnings": True,
    "extract_flat": False,
    "source_address": "0.0.0.0",
}

_FFMPEG_OPTIONS: dict[str, str] = {
    "before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5",
    "options": "-vn",
}


class YTDLSource:
    _executor = ThreadPoolExecutor(max_workers=2)

    @classmethod
    async def extract_info(cls, query: str) -> dict[str, Any]:
        loop = asyncio.get_running_loop()

        def _extract() -> dict[str, Any]:
            with yt_dlp.YoutubeDL(_YTDL_OPTIONS) as ydl:
                return ydl.extract_info(query, download=False)

        data = await loop.run_in_executor(cls._executor, _extract)
        if "entries" in data and data["entries"]:
            return data["entries"][0]
        return data

    @classmethod
    async def create_track(cls, query: str, requester: discord.Member | discord.User) -> Track:
        data = await cls.extract_info(query)

        webpage_url = data.get("webpage_url") or data.get("url")
        if not webpage_url:
            raise RuntimeError("재생 가능한 URL을 찾지 못했습니다.")

        return Track(
            title=data.get("title", "제목 없음"),
            webpage_url=webpage_url,
            duration=data.get("duration"),
            thumbnail=data.get("thumbnail"),
            requester_id=requester.id,
            requester_name=getattr(requester, "display_name", requester.name),
        )

    @classmethod
    async def create_audio_source(cls, query: str) -> discord.AudioSource:
        data = await cls.extract_info(query)
        stream_url = data.get("url")

        if not stream_url:
            raise RuntimeError("오디오 스트림 URL 추출에 실패했습니다.")

        return discord.FFmpegPCMAudio(stream_url, **_FFMPEG_OPTIONS)
