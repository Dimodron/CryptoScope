from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def main_menu_kb() -> InlineKeyboardMarkup:
    kb = [
        [
            InlineKeyboardButton(text="📊 Свечи", callback_data="an_candles"),
            InlineKeyboardButton(text="📘 Стакан", callback_data="an_orderbook"),
        ],
        [
            InlineKeyboardButton(text="📈 Объём", callback_data="an_volume"),
            InlineKeyboardButton(text="⚙️ Фьючи (funding/OI)", callback_data="an_derivatives"),
        ],
        [
            InlineKeyboardButton(text="🔗 Корреляции", callback_data="an_correlation"),
            InlineKeyboardButton(text="🧾 Полный отчёт", callback_data="an_full"),
        ],
        [
            InlineKeyboardButton(text="100 🕯", callback_data="cl_100"),
            InlineKeyboardButton(text="200 🕯", callback_data="cl_200"),
            InlineKeyboardButton(text="500 🕯", callback_data="cl_500"),
        ],
        [
            InlineKeyboardButton(text="⏱ 1h", callback_data="tf_1h"),
            InlineKeyboardButton(text="⏱ 4h", callback_data="tf_4h"),
            InlineKeyboardButton(text="⏱ 1d", callback_data="tf_1d"),
        ],
    ]
    return InlineKeyboardMarkup(inline_keyboard=kb)
