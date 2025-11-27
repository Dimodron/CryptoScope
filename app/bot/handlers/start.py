from aiogram import Router, types
from aiogram.filters import CommandStart, Command

from bot.keyboards import main_menu_kb
from services.user_settings import get_user_settings, set_symbol

router = Router()

@router.message(CommandStart())
async def cmd_start(message: types.Message):
    settings = get_user_settings(message.chat.id)
    text = (
        "Привет! Я бот-аналитик.\n\n"
        f"Текущий символ: <b>{settings.symbol}</b>\n"
        f"Таймфрейм: <b>{settings.interval}</b>\n"
        f"Свечей для анализа: <b>{settings.candles_limit}</b>\n\n"
        "Выбери тип аналитики или измени настройки.\n"
        "Символ меняется командой: <code>/symbol BTCUSDT</code>\n"
        "Помощь по боту: <code>/help</code>\n"
        "Поддержать автора: <code>/support</code>"
    )
    await message.answer(text, reply_markup=main_menu_kb())


@router.message(Command("symbol"))
async def cmd_symbol(message: types.Message):
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        await message.answer("Использование: <code>/symbol BNBUSDT</code>")
        return

    raw_symbol = parts[1].strip().upper()
    if not raw_symbol.endswith("USDT"):
        await message.answer("Символ должен быть в формате, например: <code>BNBUSDT</code>, <code>BTCUSDT</code>.")
        return

    settings = set_symbol(message.chat.id, raw_symbol)
    await message.answer(
        f"Символ обновлён: <b>{settings.symbol}</b>\n"
        f"Текущий таймфрейм: <b>{settings.interval}</b>",
        reply_markup=main_menu_kb()
    )
