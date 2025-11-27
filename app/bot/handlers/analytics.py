from aiogram import Router
from aiogram.types import CallbackQuery

from services.user_settings import get_user_settings, set_interval, set_candles_limit
from bot.keyboards import main_menu_kb

import services.analytic_service as s

router = Router()

@router.callback_query(lambda c: c.data.startswith("an_"))
async def handle_analytics_buttons(callback: CallbackQuery):
    code = callback.data
    chat_id = callback.message.chat.id
    settings = get_user_settings(chat_id)

    await callback.answer("Готовлю аналитику...")

    symbol = settings.symbol
    interval = settings.interval
    limit = settings.candles_limit

    if code == "an_candles":
        text = s.build_candle_report(symbol, interval, limit)
    elif code == "an_orderbook":
        text = s.build_orderbook_report(symbol)
    elif code == "an_volume":
        text = s.build_volume_report(symbol)
    elif code == "an_derivatives":
        text = s.build_derivatives_report(symbol)
    elif code == "an_correlation":
        text = s.build_correlation_report(symbol, interval, limit)
    elif code == "an_full":
        text = s.build_full_report(symbol, interval, limit)
    else:
        text = "Неизвестная команда."

    if len(text) > 4000:
        chunks = [text[i:i+4000] for i in range(0, len(text), 4000)]
        for chunk in chunks:
            await callback.message.answer(chunk)
    else:
        await callback.message.answer(text, reply_markup=main_menu_kb())


@router.callback_query(lambda c: c.data.startswith("tf_"))
async def handle_timeframe_buttons(callback: CallbackQuery):
    chat_id = callback.message.chat.id
    code = callback.data

    if code == "tf_1h":
        interval = "1h"
    elif code == "tf_4h":
        interval = "4h"
    elif code == "tf_1d":
        interval = "1d"
    else:
        await callback.answer("Неизвестный таймфрейм")
        return

    settings = set_interval(chat_id, interval)
    await callback.answer(f"Таймфрейм: {settings.interval}", show_alert=False)

    await callback.message.answer(
        f"Таймфрейм обновлён: <b>{settings.interval}</b>\n"
        f"Символ: <b>{settings.symbol}</b>\n"
        f"Свечей для анализа: <b>{settings.candles_limit}</b>",
        reply_markup=main_menu_kb()
    )


@router.callback_query(lambda c: c.data.startswith("cl_"))
async def handle_candles_limit_buttons(callback: CallbackQuery):
    chat_id = callback.message.chat.id
    code = callback.data

    if code == "cl_100":
        limit = 100
    elif code == "cl_200":
        limit = 200
    elif code == "cl_500":
        limit = 500
    else:
        await callback.answer("Неизвестное количество свечей")
        return

    settings = set_candles_limit(chat_id, limit)
    await callback.answer(f"Свечей: {settings.candles_limit}", show_alert=False)

    await callback.message.answer(
        f"Количество свечей обновлено: <b>{settings.candles_limit}</b>\n"
        f"Символ: <b>{settings.symbol}</b>\n"
        f"Таймфрейм: <b>{settings.interval}</b>",
        reply_markup=main_menu_kb()
    )
