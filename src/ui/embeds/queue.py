from __future__ import annotations

import discord


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
