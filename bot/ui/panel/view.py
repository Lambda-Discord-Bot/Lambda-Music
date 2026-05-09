from __future__ import annotations

import discord

from bot.music.manager import MusicManager
from bot.ui.embeds import build_panel_embed, build_queue_embed
from bot.ui.modals import PlayModal
from bot.ui.panel.voice_checks import get_author_voice_channel


class MusicPanelView(discord.ui.View):
    def __init__(self, manager: MusicManager) -> None:
        super().__init__(timeout=None)
        self.manager = manager

    async def _refresh_panel(self, interaction: discord.Interaction) -> None:
        if interaction.guild is None:
            return
        self._register_current_panel(interaction)
        player = self.manager.get_player(interaction.guild)
        embed = build_panel_embed(player)
        try:
            if interaction.message:
                await interaction.message.edit(embed=embed, view=self)
        except discord.HTTPException:
            pass

    def _register_current_panel(self, interaction: discord.Interaction) -> None:
        if interaction.guild is None or interaction.message is None:
            return
        self.manager.register_panel_message(
            interaction.guild.id,
            interaction.message.channel.id,
            interaction.message.id,
        )

    async def _require_voice(self, interaction: discord.Interaction) -> discord.VoiceChannel | None:
        channel = get_author_voice_channel(interaction)
        if channel is None:
            await interaction.response.send_message("먼저 음성 채널에 접속해주세요.", ephemeral=True)
            return None
        return channel

    @discord.ui.button(label="재생", style=discord.ButtonStyle.success, custom_id="lambda:play")
    async def play_button(self, interaction: discord.Interaction, _: discord.ui.Button) -> None:
        self._register_current_panel(interaction)
        await interaction.response.send_modal(PlayModal(self.manager))

    @discord.ui.button(label="일시정지", style=discord.ButtonStyle.secondary, custom_id="lambda:pause")
    async def pause_button(self, interaction: discord.Interaction, _: discord.ui.Button) -> None:
        self._register_current_panel(interaction)
        if interaction.guild is None:
            await interaction.response.send_message("서버에서만 사용할 수 있습니다.", ephemeral=True)
            return

        if await self._require_voice(interaction) is None:
            return

        player = self.manager.get_player(interaction.guild)
        paused = await player.pause()
        await interaction.response.send_message("일시정지되었습니다." if paused else "재생 중인 곡이 없습니다.", ephemeral=True)
        await self._refresh_panel(interaction)

    @discord.ui.button(label="다시재생", style=discord.ButtonStyle.secondary, custom_id="lambda:resume")
    async def resume_button(self, interaction: discord.Interaction, _: discord.ui.Button) -> None:
        self._register_current_panel(interaction)
        if interaction.guild is None:
            await interaction.response.send_message("서버에서만 사용할 수 있습니다.", ephemeral=True)
            return

        if await self._require_voice(interaction) is None:
            return

        player = self.manager.get_player(interaction.guild)
        resumed = await player.resume()
        await interaction.response.send_message("재생을 다시 시작했습니다." if resumed else "일시정지된 곡이 없습니다.", ephemeral=True)
        await self._refresh_panel(interaction)

    @discord.ui.button(label="스킵", style=discord.ButtonStyle.primary, custom_id="lambda:skip")
    async def skip_button(self, interaction: discord.Interaction, _: discord.ui.Button) -> None:
        self._register_current_panel(interaction)
        if interaction.guild is None:
            await interaction.response.send_message("서버에서만 사용할 수 있습니다.", ephemeral=True)
            return

        if await self._require_voice(interaction) is None:
            return

        player = self.manager.get_player(interaction.guild)
        skipped = await player.skip()
        await interaction.response.send_message("현재 곡을 스킵했습니다." if skipped else "스킵할 곡이 없습니다.", ephemeral=True)
        await self._refresh_panel(interaction)

    @discord.ui.button(label="정지", style=discord.ButtonStyle.danger, custom_id="lambda:stop")
    async def stop_button(self, interaction: discord.Interaction, _: discord.ui.Button) -> None:
        self._register_current_panel(interaction)
        if interaction.guild is None:
            await interaction.response.send_message("서버에서만 사용할 수 있습니다.", ephemeral=True)
            return

        if await self._require_voice(interaction) is None:
            return

        player = self.manager.get_player(interaction.guild)
        await player.stop()
        await interaction.response.send_message("재생을 정지하고 대기열을 비웠습니다.", ephemeral=True)
        await self._refresh_panel(interaction)

    @discord.ui.button(label="대기열", style=discord.ButtonStyle.primary, custom_id="lambda:queue")
    async def queue_button(self, interaction: discord.Interaction, _: discord.ui.Button) -> None:
        self._register_current_panel(interaction)
        if interaction.guild is None:
            await interaction.response.send_message("서버에서만 사용할 수 있습니다.", ephemeral=True)
            return

        player = self.manager.get_player(interaction.guild)
        items = await player.queue_snapshot()
        embed = build_queue_embed(items, player.current)
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @discord.ui.button(label="반복", style=discord.ButtonStyle.secondary, custom_id="lambda:repeat")
    async def repeat_button(self, interaction: discord.Interaction, _: discord.ui.Button) -> None:
        self._register_current_panel(interaction)
        if interaction.guild is None:
            await interaction.response.send_message("서버에서만 사용할 수 있습니다.", ephemeral=True)
            return

        player = self.manager.get_player(interaction.guild)
        mode = await player.toggle_repeat()
        await interaction.response.send_message(f"반복 모드: **{mode.label}**", ephemeral=True)
        await self._refresh_panel(interaction)

    @discord.ui.button(label="셔플", style=discord.ButtonStyle.secondary, custom_id="lambda:shuffle")
    async def shuffle_button(self, interaction: discord.Interaction, _: discord.ui.Button) -> None:
        self._register_current_panel(interaction)
        if interaction.guild is None:
            await interaction.response.send_message("서버에서만 사용할 수 있습니다.", ephemeral=True)
            return

        player = self.manager.get_player(interaction.guild)
        await player.shuffle()
        await interaction.response.send_message("대기열 순서를 랜덤으로 섞었습니다.", ephemeral=True)
        await self._refresh_panel(interaction)

    @discord.ui.button(label="나가기", style=discord.ButtonStyle.danger, custom_id="lambda:leave")
    async def leave_button(self, interaction: discord.Interaction, _: discord.ui.Button) -> None:
        self._register_current_panel(interaction)
        if interaction.guild is None:
            await interaction.response.send_message("서버에서만 사용할 수 있습니다.", ephemeral=True)
            return

        player = self.manager.get_player(interaction.guild)
        left = await player.leave()
        await interaction.response.send_message(
            "음성 채널에서 나갔습니다." if left else "현재 접속 중인 음성 채널이 없습니다.",
            ephemeral=True,
        )
        await self._refresh_panel(interaction)
