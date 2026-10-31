import asyncio
import logging
import os

from aiogram import Bot, Dispatcher

from bot.handlers import router
from db.profiles import init_db

# Токен берем из переменной окружения. 
# Если запускаете локально, введите токен в кавычки вместо YOUR_TOKEN_HERE.
BOT_TOKEN = os.getenv("BOT_TOKEN", "YOUR_TOKEN_HERE")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)


async def main():
    # Инициализируем базу данных профилей
    init_db()
    
    # Создаем бота и диспетчер
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()
    
    # Подключаем обработчики
    dp.include_router(router)
    
    logging.info("Telegram bot starting...")
    
    # Запускаем бесконечный цикл опроса Telegram
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())