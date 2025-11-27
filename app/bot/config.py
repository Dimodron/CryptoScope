from os import environ
from dataclasses import dataclass

@dataclass
class BotConfig:
    token: str

def load_config() -> BotConfig:
    token = environ.get("TELEGRAM_BOT_TOKEN")
    if not token:
        raise RuntimeError("TELEGRAM_BOT_TOKEN is not set")
    return BotConfig(token=token)
