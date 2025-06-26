import json
import os
import sys
import asyncio
from typing import Dict, Any

# Добавляем путь к основному проекту
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

# Инициализация переменных окружения
BOT_TOKEN = os.getenv('BOT_TOKEN')
MONGODB_URL = os.getenv('MONGODB_URL', 'mongodb+srv://alexvampire888:OUP5TdEvO9V0sryq@cluster0.gxvexo3.mongodb.net/')
DATABASE_NAME = os.getenv('DATABASE_NAME', 'turan_bot')

def handler(event: Dict[str, Any], context=None) -> Dict[str, Any]:
    """Vercel webhook handler for Telegram bot"""
    try:
        # Получаем данные запроса
        method = event.get('httpMethod', event.get('method', 'GET'))
        body = event.get('body', '')
        headers = event.get('headers', {})
        
        print(f"Webhook called: method={method}")
        print(f"Headers: {headers}")
        print(f"Body: {body}")
        
        # Для GET запросов возвращаем статус
        if method == 'GET':
            return {
                'statusCode': 200,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({
                    "status": "ok",
                    "message": "Telegram webhook endpoint",
                    "bot_token_exists": bool(BOT_TOKEN),
                    "mongodb_url_exists": bool(MONGODB_URL)
                })
            }
        
        # Для POST запросов обрабатываем Telegram updates
        if method == 'POST':
            # Парсим JSON данные
            try:
                if isinstance(body, str):
                    update_data = json.loads(body) if body else {}
                else:
                    update_data = body or {}
            except json.JSONDecodeError as e:
                print(f"JSON decode error: {e}")
                return {
                    'statusCode': 400,
                    'headers': {'Content-Type': 'application/json'},
                    'body': json.dumps({"error": "Invalid JSON"})
                }
            
            # Проверяем наличие обязательных данных
            if not BOT_TOKEN:
                return {
                    'statusCode': 500,
                    'headers': {'Content-Type': 'application/json'},
                    'body': json.dumps({"error": "BOT_TOKEN not configured"})
                }
            
            # Обрабатываем Telegram update асинхронно
            try:
                result = asyncio.run(process_telegram_update(update_data))
                return {
                    'statusCode': 200,
                    'headers': {'Content-Type': 'application/json'},
                    'body': json.dumps(result)
                }
            except Exception as e:
                print(f"Error processing update: {e}")
                return {
                    'statusCode': 500,
                    'headers': {'Content-Type': 'application/json'},
                    'body': json.dumps({"error": str(e)})
                }
        
        # Неподдерживаемый метод
        return {
            'statusCode': 405,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({"error": "Method not allowed"})
        }
        
    except Exception as e:
        print(f"Handler error: {e}")
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({"error": str(e)})
        }

async def process_telegram_update(update_data: Dict[str, Any]) -> Dict[str, str]:
    """Обрабатывает Telegram update"""
    try:
        # Простая обработка для тестирования
        message_text = ""
        chat_id = None
        
        # Извлекаем данные из update
        if 'message' in update_data:
            message = update_data['message']
            message_text = message.get('text', '')
            chat_id = message.get('chat', {}).get('id')
        elif 'callback_query' in update_data:
            callback = update_data['callback_query']
            message_text = callback.get('data', '')
            chat_id = callback.get('message', {}).get('chat', {}).get('id')
        
        print(f"Processing update: chat_id={chat_id}, text='{message_text}'")
        
        # Пока просто возвращаем статус получения
        return {
            "status": "ok",
            "message": "Update processed",
            "chat_id": str(chat_id) if chat_id else None,
            "text": message_text
        }
        
    except Exception as e:
        print(f"Error in process_telegram_update: {e}")
        return {
            "status": "error",
            "message": str(e)
        }

# Для совместимости с разными форматами вызовов
def handler_func(event, context=None):
    """Alternative handler name"""
    return handler(event, context)

# Экспортируем обе версии
__all__ = ['handler', 'handler_func'] 