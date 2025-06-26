import asyncio

from aiogram import Bot, Dispatcher, F
from aiogram.enums import ParseMode
from aiogram.types import Message

from app.config import settings
from app.database import connect_to_mongo, close_mongo_connection

# Import routers (to be created)
from app.routers import auth, catalog, order, stock, analytics, menu


def register_routers(dp: Dispatcher):
    dp.include_router(auth.router)
    dp.include_router(menu.router)
    dp.include_router(catalog.router)
    dp.include_router(order.router)
    dp.include_router(stock.router)
    dp.include_router(analytics.router)


async def on_startup(bot: Bot):
    print("Bot started")


async def main():
    # Подключение к MongoDB
    await connect_to_mongo()
    
    try:
        bot = Bot(token=settings.bot_token, parse_mode=ParseMode.HTML)
        dp = Dispatcher()
        register_routers(dp)

        await dp.start_polling(bot, on_startup=on_startup)
    finally:
        await bot.session.close()
        await close_mongo_connection()


if __name__ == "__main__":
    asyncio.run(main()) 