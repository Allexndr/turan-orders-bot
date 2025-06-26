import asyncio
import json
import os
import sys
import traceback

# Добавляем путь к основному проекту
sys.path.append('/var/task')

# Инициализация переменных окружения
BOT_TOKEN = os.getenv('BOT_TOKEN')
MONGODB_URL = os.getenv('MONGODB_URL', 'mongodb://localhost:27017')
DATABASE_NAME = os.getenv('DATABASE_NAME', 'turan_bot')

def handler(event, context=None):
    """Vercel handler function"""
    try:
        # Получаем метод запроса
        method = event.get('httpMethod') or event.get('method', 'GET')
        headers = event.get('headers', {})
        body = event.get('body', '')
        
        print(f"Handler called with method: {method}")
        print(f"Headers: {headers}")
        print(f"BOT_TOKEN exists: {bool(BOT_TOKEN)}")
        
        # Обработка POST запросов (вебхуки от Telegram)
        if method == 'POST':
            print("Processing POST request...")
            print(f"Body: {body}")
            
            # Парсим JSON если есть
            try:
                if body:
                    update_data = json.loads(body) if isinstance(body, str) else body
                    print(f"Parsed update: {update_data}")
                else:
                    update_data = {}
            except json.JSONDecodeError as e:
                print(f"JSON decode error: {e}")
                update_data = {}
            
            response_data = {
                "status": "ok", 
                "message": "Webhook received POST request",
                "bot_token_exists": bool(BOT_TOKEN),
                "mongodb_url_exists": bool(MONGODB_URL),
                "update_received": bool(update_data)
            }
            
            return {
                'statusCode': 200,
                'headers': {
                    'Content-Type': 'application/json',
                },
                'body': json.dumps(response_data)
            }
        
        # Обработка GET запросов (тестирование)
        else:
            print("Processing GET request...")
            
            response_data = {
                "status": "ok", 
                "message": "Webhook endpoint working!",
                "method": method,
                "bot_token_exists": bool(BOT_TOKEN)
            }
            
            return {
                'statusCode': 200,
                'headers': {
                    'Content-Type': 'application/json',
                },
                'body': json.dumps(response_data)
            }
            
    except Exception as e:
        error_msg = f"Handler error: {str(e)}"
        print(f"ERROR: {error_msg}")
        print(f"Traceback: {traceback.format_exc()}")
        
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
            },
            'body': json.dumps({"error": error_msg, "traceback": traceback.format_exc()})
        }

# Для совместимости с разными форматами вызовов
def handler_func(event, context=None):
    """Alternative handler name"""
    return handler(event, context)

# Экспортируем обе версии
__all__ = ['handler', 'handler_func'] 