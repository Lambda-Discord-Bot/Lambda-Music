from __future__ import annotations

import asyncio
from collections import deque
import random

from src.music.models import Track


class MusicQueue:
    def __init__(self) -> None:
        self._queue: deque[Track] = deque()
        self._lock = asyncio.Lock()
        self._not_empty = asyncio.Event()

    async def put(self, track: Track) -> None:
        async with self._lock:
            self._queue.append(track)
            self._not_empty.set()

    async def get(self) -> Track:
        while True:
            await self._not_empty.wait()
            async with self._lock:
                if not self._queue:
                    self._not_empty.clear()
                    continue

                track = self._queue.popleft()
                if not self._queue:
                    self._not_empty.clear()
                return track

    async def push_front(self, track: Track) -> None:
        async with self._lock:
            self._queue.appendleft(track)
            self._not_empty.set()

    async def clear(self) -> None:
        async with self._lock:
            self._queue.clear()
            self._not_empty.clear()

    async def shuffle(self) -> None:
        async with self._lock:
            items = list(self._queue)
            random.shuffle(items)
            self._queue = deque(items)
            if self._queue:
                self._not_empty.set()
            else:
                self._not_empty.clear()

    async def snapshot(self) -> list[Track]:
        async with self._lock:
            return list(self._queue)

    def peek(self) -> Track | None:
        if not self._queue:
            return None
        return self._queue[0]

    async def __len__(self) -> int:
        async with self._lock:
            return len(self._queue)

