from __future__ import annotations

from pathlib import Path

import discord

PANEL_THUMBNAIL_FILENAME = "panel_thumbnail.png"
PANEL_THUMBNAIL_ATTACHMENT_URL = f"attachment://{PANEL_THUMBNAIL_FILENAME}"


def panel_thumbnail_path() -> Path:
    project_root = Path(__file__).resolve().parents[2]
    return project_root / "assets" / PANEL_THUMBNAIL_FILENAME


def build_panel_thumbnail_file() -> discord.File | None:
    file_path = panel_thumbnail_path()
    if not file_path.exists():
        return None
    return discord.File(file_path, filename=PANEL_THUMBNAIL_FILENAME)
