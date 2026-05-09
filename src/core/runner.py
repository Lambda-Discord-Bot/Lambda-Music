from __future__ import annotations

from src.core.client import LambdaMusicBot
from src.core.logging_setup import configure_logging
from src.core.settings import load_settings


def run_bot() -> None:
    configure_logging()
    settings = load_settings()
    bot = LambdaMusicBot(settings)
    bot.run(settings.token, log_handler=None)

