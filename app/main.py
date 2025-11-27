import asyncio
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties

from bot.config import load_config
from bot.handlers import all_routers


async def main():
    config = load_config()

    bot = Bot(
        token=config.token,
        default=DefaultBotProperties(parse_mode="HTML")
    )

    dp = Dispatcher()

    for router in all_routers:
        dp.include_router(router)

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
