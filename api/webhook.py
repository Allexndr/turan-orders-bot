import asyncio
import json
import os
from aiogram import Bot, Dispatcher
from aiogram.types import Update

# Инициализация переменных окружения
BOT_TOKEN = os.getenv('BOT_TOKEN')
MONGODB_URL = os.getenv('MONGODB_URL', 'mongodb://localhost:27017')
DATABASE_NAME = os.getenv('DATABASE_NAME', 'turan_bot')

# Создаем бота
bot = Bot(token=BOT_TOKEN) if BOT_TOKEN else None
dp = Dispatcher()

# Глобальная переменная для отслеживания инициализации
initialized = False

async def initialize_bot():
    """Инициализация бота и подключений"""
    global initialized
    if initialized or not BOT_TOKEN:
        return
    
    try:
        # Импортируем и регистрируем роутеры только при инициализации
        from app.routers import auth, catalog, order, stock, analytics, menu
        from app.database import connect_to_mongo
        
        # Подключаемся к MongoDB
        await connect_to_mongo()
        
        # Регистрируем роутеры
        dp.include_router(auth.router)
        dp.include_router(menu.router)
        dp.include_router(catalog.router)
        dp.include_router(order.router)
        dp.include_router(stock.router)
        dp.include_router(analytics.router)
        
        initialized = True
        print("Bot initialized successfully")
        
    except Exception as e:
        print(f"Error initializing bot: {e}")
        raise

async def process_update(data):
    """Обработка обновления от Telegram"""
    try:
        if not bot:
            return {"error": "Bot token not configured"}
            
        # Инициализируем бота если еще не сделали
        await initialize_bot()
        
        # Создаем объект Update
        update = Update(**data)
        
        # Обрабатываем обновление
        await dp.feed_update(bot, update)
        
        return {"status": "ok"}
        
    except Exception as e:
        print(f"Error processing update: {e}")
        return {"error": str(e)}

def handler(request):
    """Обработчик для Vercel"""
    try:
        # Получаем тело запроса
        if hasattr(request, 'get_json'):
            # Flask-style request
            data = request.get_json(force=True)
        elif hasattr(request, 'json'):
            # FastAPI-style request  
            data = request.json()
        else:
            # Vercel request object
            body = getattr(request, 'body', '')
            if isinstance(body, bytes):
                body = body.decode('utf-8')
            elif isinstance(body, str) and body:
                pass
            else:
                body = json.dumps(request) if hasattr(request, '__dict__') else '{}'
            
            data = json.loads(body) if body else {}
        
        # Обрабатываем обновление
        result = asyncio.run(process_update(data))
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps(result)
        }
        
    except Exception as e:
        error_msg = f"Handler error: {str(e)}"
        print(error_msg)
        
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({"error": error_msg})
        } 