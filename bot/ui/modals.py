from __future__ import annotations

import discord

from bot.music.manager import MusicManager


class PlayModal(discord.ui.Modal, title="음악 재생"):
    query = discord.ui.TextInput(
        label="유튜브 링크 또는 검색어",
        placeholder="예) NewJeans - Ditto",
        max_length=400,
        required=True,
    )

    def __init__(self, manager: MusicManager) -> None:
        super().__init__(timeout=180)
        self.manager = manager

    async def on_submit(self, interaction: discord.Interaction) -> None:
        await interaction.response.defer(ephemeral=True, thinking=True)

        if interaction.guild is None:
            await interaction.followup.send("서버에서만 사용할 수 있습니다.", ephemeral=True)
            return

        if not isinstance(interaction.user, discord.Member):
            await interaction.followup.send("멤버 정보 확인에 실패했습니다.", ephemeral=True)
            return

        if interaction.user.voice is None or interaction.user.voice.channel is None:
            await interaction.followup.send("먼저 음성 채널에 접속해주세요.", ephemeral=True)
            return

        player = self.manager.get_player(interaction.guild)

        try:
            await player.connect(interaction.user.voice.channel)
            track = await player.enqueue(self.query.value, interaction.user)
        except Exception as exc:
            await interaction.followup.send(f"재생 요청 실패: {exc}", ephemeral=True)
            return

        await interaction.followup.send(
            f"대기열에 추가됨: **{track.title}** ({track.duration_text})",
            ephemeral=True,
        )
