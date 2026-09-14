"""環境変数の読み込み設定。"""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

# プロジェクトルートの .env を読み込む（既に環境変数が設定されている場合はそちらを優先）
_ENV_PATH = Path(__file__).resolve().parents[2] / ".env"
load_dotenv(dotenv_path=_ENV_PATH, override=False)


class ConfigError(RuntimeError):
    """必須の環境変数が不足している場合に送出する。"""


@dataclass(frozen=True)
class Settings:
    ops_consumer_key: str
    ops_consumer_secret: str
    ops_base_url: str


def get_settings() -> Settings:
    consumer_key = os.environ.get("OPS_CONSUMER_KEY", "").strip()
    consumer_secret = os.environ.get("OPS_CONSUMER_SECRET", "").strip()
    base_url = os.environ.get("OPS_BASE_URL", "https://ops.epo.org/3.2").strip()

    if not consumer_key or not consumer_secret:
        raise ConfigError(
            "OPS_CONSUMER_KEY / OPS_CONSUMER_SECRET が設定されていません。"
            ".env に EPO OPS のConsumer Key/Secretを記入してください"
            "（未登録の場合は https://developers.epo.org でアプリを登録してください）。"
        )

    return Settings(
        ops_consumer_key=consumer_key,
        ops_consumer_secret=consumer_secret,
        ops_base_url=base_url,
    )
