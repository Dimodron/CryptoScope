from dataclasses import dataclass
from typing import Dict


@dataclass
class UserSettings:
    symbol: str = "BNBUSDT"
    interval: str = "1h"
    candles_limit: int = 100


_user_settings: Dict[int, UserSettings] = {}


def get_user_settings(chat_id: int) -> UserSettings:
    if chat_id not in _user_settings:
        _user_settings[chat_id] = UserSettings()
    return _user_settings[chat_id]


def set_symbol(chat_id: int, symbol: str) -> UserSettings:
    settings = get_user_settings(chat_id)
    settings.symbol = symbol.upper()
    return settings


def set_interval(chat_id: int, interval: str) -> UserSettings:
    settings = get_user_settings(chat_id)
    settings.interval = interval
    return settings


def set_candles_limit(chat_id: int, limit: int) -> UserSettings:
    settings = get_user_settings(chat_id)
    settings.candles_limit = limit
    return settings
