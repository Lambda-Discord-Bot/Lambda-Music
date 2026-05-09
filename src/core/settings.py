from __future__ import annotations

from dataclasses import dataclass
import os
from pathlib import Path

from dotenv import dotenv_values, load_dotenv


@dataclass(frozen=True)
class Settings:
    token: str


def load_settings() -> Settings:
    project_root = Path(__file__).resolve().parents[2]
    env_path = project_root / ".env"

    token = ""
    if env_path.exists():
        values = dotenv_values(env_path, encoding="utf-8-sig")
        token = str(values.get("DISCORD_TOKEN", "")).strip()

    if not token:
        load_dotenv(dotenv_path=env_path, encoding="utf-8-sig")
        token = os.getenv("DISCORD_TOKEN", "").strip()

    if not token:
        raise RuntimeError(
            f"DISCORD_TOKEN 이 설정되지 않았습니다. {env_path} 파일을 확인하세요."
        )

    return Settings(token=token)
