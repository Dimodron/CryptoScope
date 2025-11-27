from aiogram import Router, types
from aiogram.filters import Command

from bot.keyboards import main_menu_kb

router = Router()

@router.message(Command("support"))
async def cmd_support(message: types.Message):
    text = (
        "Вы можете поддержать автора, если вам понравился бот:\n\n"
        "<b>Сбербанк:</b> <code>+79687341924</code>\n"
    )
    await message.answer(text, reply_markup=main_menu_kb())
