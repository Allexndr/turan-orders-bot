import asyncio
import json
from aiogram import Bot, Dispatcher
from aiogram.types import Update
from aiogram.webhook.aiohttp_server import SimpleRequestHandler

from app.config import settings
from app.database import connect_to_mongo
from main import register_routers

# Инициализация бота и диспетчера
bot = Bot(token=settings.bot_token)
dp = Dispatcher()
register_routers(dp)

# Подключение к MongoDB при старте
asyncio.create_task(connect_to_mongo())

async def handler(request):
    """Обработчик веб-хуков от Telegram"""
    try:
        # Получаем данные от Telegram
        data = await request.json()
        
        # Создаем объект Update
        update = Update(**data)
        
        # Обрабатываем обновление
        await dp.feed_update(bot, update)
        
        return {"status": "ok"}
    except Exception as e:
        print(f"Error in webhook: {e}")
        return {"error": str(e)}, 500

# Для Vercel
def main(request):
    """Главная функция для Vercel"""
    return asyncio.run(handler(request)) 