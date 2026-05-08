from __future__ import annotations

import discord

from bot.music.player import GuildMusicPlayer
from bot.ui.panel_assets import PANEL_THUMBNAIL_ATTACHMENT_URL


def build_panel_embed(player: GuildMusicPlayer) -> discord.Embed:
    embed = discord.Embed(
        title="Lambda Music Panel",
        description="버튼으로 음악을 제어하세요.",
        color=discord.Color.blurple(),
    )
    embed.set_thumbnail(url=PANEL_THUMBNAIL_ATTACHMENT_URL)

    if player.current:
        track = player.current
        embed.add_field(name="현재 재생", value=f"[{track.title}]({track.webpage_url})", inline=False)
        embed.add_field(name="길이", value=track.duration_text, inline=True)
        embed.add_field(name="요청자", value=track.requester_name, inline=True)
        if track.thumbnail:
            embed.set_image(url=track.thumbnail)
    else:
        embed.add_field(name="현재 재생", value="재생 중인 곡이 없습니다.", inline=False)

    next_track = player.queue.peek()
    next_value = "없음"
    if next_track is not None:
        next_value = f"[{next_track.title}]({next_track.webpage_url})"

    embed.add_field(name="반복 모드", value=player.repeat_mode.label, inline=True)
    embed.add_field(name="다음 대기곡", value=next_value, inline=True)
    embed.set_footer(text="재생 버튼으로 유튜브 링크 또는 검색어를 입력할 수 있습니다.")
    return embed


def build_queue_embed(items: list, current) -> discord.Embed:
    embed = discord.Embed(title="현재 대기열", color=discord.Color.green())

    if current:
        embed.add_field(name="지금 재생", value=f"[{current.title}]({current.webpage_url})", inline=False)

    if not items:
        embed.description = "대기열이 비어 있습니다."
        return embed

    lines: list[str] = []
    for idx, track in enumerate(items[:20], start=1):
        lines.append(f"`{idx:02}` [{track.title}]({track.webpage_url}) ({track.duration_text})")

    embed.description = "\n".join(lines)
    if len(items) > 20:
        embed.set_footer(text=f"총 {len(items)}곡 중 20곡만 표시됩니다.")
    return embed
