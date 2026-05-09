from __future__ import annotations

import discord


def get_author_voice_channel(interaction: discord.Interaction) -> discord.VoiceChannel | None:
    if not isinstance(interaction.user, discord.Member):
        return None
    if interaction.user.voice is None:
        return None
    if not isinstance(interaction.user.voice.channel, discord.VoiceChannel):
        return None
    return interaction.user.voice.channel
