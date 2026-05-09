from __future__ import annotations

from bot.core.client import LambdaMusicBot
from bot.core.logging_setup import configure_logging
from bot.core.settings import load_settings


def run_bot() -> None:
    configure_logging()
    settings = load_settings()
    bot = LambdaMusicBot(settings)
    bot.run(settings.token, log_handler=None)
