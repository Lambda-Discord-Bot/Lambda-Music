from __future__ import annotations

import discord
from discord import app_commands
from discord.ext import commands

from bot.ui.embeds import build_panel_embed
from bot.ui.panel_assets import build_panel_thumbnail_file
from bot.ui.views import MusicPanelView


class MusicPanelCog(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @app_commands.command(name="람다음악패널", description="선택한 채널에 음악 제어 패널을 설치합니다.")
    @app_commands.describe(channel="패널을 설치할 텍스트 채널")
    @app_commands.default_permissions(manage_guild=True)
    async def lambda_music_panel(
        self,
        interaction: discord.Interaction,
        channel: discord.TextChannel | None = None,
    ) -> None:
        if interaction.guild is None:
            await interaction.response.send_message("서버에서만 사용할 수 있습니다.", ephemeral=True)
            return

        target_channel = channel or interaction.channel
        if not isinstance(target_channel, discord.TextChannel):
            await interaction.response.send_message("텍스트 채널을 지정해주세요.", ephemeral=True)
            return

        me = interaction.guild.me
        if me is None:
            await interaction.response.send_message("봇 멤버 정보를 불러오지 못했습니다.", ephemeral=True)
            return

        perms = target_channel.permissions_for(me)
        if not perms.send_messages or not perms.embed_links:
            await interaction.response.send_message(
                "해당 채널에 메시지/임베드 전송 권한이 없습니다.",
                ephemeral=True,
            )
            return

        player = self.bot.music_manager.get_player(interaction.guild)
        embed = build_panel_embed(player)
        view = MusicPanelView(self.bot.music_manager)
        thumb_file = build_panel_thumbnail_file()

        if thumb_file is not None:
            panel_message = await target_channel.send(embed=embed, view=view, file=thumb_file)
        else:
            panel_message = await target_channel.send(embed=embed, view=view)
        self.bot.music_manager.register_panel_message(
            interaction.guild.id,
            target_channel.id,
            panel_message.id,
        )
        await interaction.response.send_message(
            f"음악 패널을 {target_channel.mention} 채널에 설치했습니다.",
            ephemeral=True,
        )


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(MusicPanelCog(bot))
