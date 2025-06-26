import asyncio
import json
import os
from aiogram import Bot, Dispatcher
from aiogram.types import Update

from app.config import settings
from app.database import connect_to_mongo

# Import routers
from app.routers import auth, catalog, order, stock, analytics, menu

# Инициализация бота и диспетчера
bot = Bot(token=settings.bot_token)
dp = Dispatcher()

# Register routers
def register_routers(dp: Dispatcher):
    dp.include_router(auth.router)
    dp.include_router(menu.router)
    dp.include_router(catalog.router)
    dp.include_router(order.router)
    dp.include_router(stock.router)
    dp.include_router(analytics.router)

register_routers(dp)

# Глобальная переменная для отслеживания подключения к MongoDB
mongo_connected = False

async def ensure_mongo_connection():
    global mongo_connected
    if not mongo_connected:
        await connect_to_mongo()
        mongo_connected = True

async def process_webhook(data):
    """Обработка webhook от Telegram"""
    try:
        # Подключаемся к MongoDB если еще не подключены
        await ensure_mongo_connection()
        
        # Создаем объект Update
        update = Update(**data)
        
        # Обрабатываем обновление
        await dp.feed_update(bot, update)
        
        return {"status": "ok"}
    except Exception as e:
        print(f"Error processing webhook: {e}")
        return {"error": str(e)}

def handler(request):
    """Главная функция для Vercel"""
    try:
        # Парсим JSON из тела запроса
        if hasattr(request, 'get_json'):
            data = request.get_json()
        else:
            # Для случая когда request это dict
            body = request.get('body', '')
            if isinstance(body, str):
                data = json.loads(body)
            else:
                data = body
        
        # Обрабатываем webhook асинхронно
        result = asyncio.run(process_webhook(data))
        
        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps(result)
        }
        
    except Exception as e:
        print(f"Error in handler: {e}")
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({"error": str(e)})
        } 