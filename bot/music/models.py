from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class RepeatMode(str, Enum):
    OFF = "off"
    ONE = "one"
    ALL = "all"

    def next_mode(self) -> "RepeatMode":
        if self is RepeatMode.OFF:
            return RepeatMode.ONE
        if self is RepeatMode.ONE:
            return RepeatMode.ALL
        return RepeatMode.OFF

    @property
    def label(self) -> str:
        if self is RepeatMode.OFF:
            return "끔"
        if self is RepeatMode.ONE:
            return "한 곡 반복"
        return "전체 반복"


@dataclass(slots=True)
class Track:
    title: str
    webpage_url: str
    duration: int | None
    thumbnail: str | None
    requester_id: int
    requester_name: str

    @property
    def duration_text(self) -> str:
        if self.duration is None:
            return "알 수 없음"

        minutes, seconds = divmod(self.duration, 60)
        hours, minutes = divmod(minutes, 60)

        if hours:
            return f"{hours:02}:{minutes:02}:{seconds:02}"
        return f"{minutes:02}:{seconds:02}"
