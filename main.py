import asyncio
import logging
import os

from aiogram import Bot, Dispatcher

from bot.handlers import router
from db.profiles import init_db

BOT_TOKEN = os.getenv("BOT_TOKEN", "YOUR_TOKEN_HERE")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)


async def main():
    init_db()
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()
    dp.include_router(router)
    logging.info("Bot starting...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())