import logging
import asyncio
from config import TOKEN
from aiogram.client.default import DefaultBotProperties
from aiogram import Bot, Dispatcher
from handlers import main_router


async def main():
    logging.basicConfig(level=logging.INFO)

    bot = Bot(
        token=TOKEN,
        default=DefaultBotProperties(parse_mode='html')
    )

    dp = Dispatcher()

    dp.include_routers(main_router)

    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
