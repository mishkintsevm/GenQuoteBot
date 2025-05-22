import asyncio
import os
import logging

from dotenv import load_dotenv

from aiogram import Bot, Dispatcher
from aiogram.types import BotCommand

from handlers.menu_router import menu_router


# Загрузка .env (файл для хранения конфиденциальных данных)
load_dotenv()
TOKEN = os.getenv("TG_TOKEN")
if not TOKEN:
    raise RuntimeError("Не удалось получить TG_TOKEN из файла .env")


# Логирование (отслеживание состояния бота)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s:%(lineno)d | %(message)s",
)
logger = logging.getLogger(__name__)


# Инициализация Bot и Dispatcher
bot = Bot(token=TOKEN)
dp = Dispatcher()


# Роутеры (модули menu_router.py)
dp.include_router(menu_router)


# Хуки запуска и остановки
async def on_startup() -> None:
    logger.info("Запуск GenQuoteBot…")
    await bot.set_my_commands([
        BotCommand(command="start", description="Запустить меню"),
        BotCommand(command="quote", description="Случайная цитата")
    ])
    logger.info("Команды подключены")

async def on_shutdown() -> None:
    logger.info("GenQuoteBot остановлен")
    await bot.session.close()
    logger.info("Сессия Telegram Bot API закрыта.")


dp.startup.register(on_startup)
dp.shutdown.register(on_shutdown)


# drop_pending_updates- не обрабатывать команды, которые были присланы, когда бот был выключен
async def main():
    logger.info("Запуск polling…")
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())


if __name__ == "__main__":
    asyncio.run(main())
