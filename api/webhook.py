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

def handler(request, context=None):
    """Vercel handler function"""
    try:
        print(f"Handler called with method: {request.get('method', 'UNKNOWN')}")
        print(f"BOT_TOKEN exists: {bool(BOT_TOKEN)}")
        
        # Обработка POST запросов (вебхуки от Telegram)
        if request.get('method') == 'POST':
            print("Processing POST request...")
            
            response_data = {
                "status": "ok", 
                "message": "Webhook working!",
                "bot_token_exists": bool(BOT_TOKEN),
                "mongodb_url_exists": bool(MONGODB_URL)
            }
            
            return {
                'statusCode': 200,
                'headers': {
                    'Content-Type': 'application/json',
                },
                'body': json.dumps(response_data)
            }
        
        # Обработка GET запросов (тестирование)
        elif request.get('method') == 'GET':
            print("Processing GET request...")
            
            response_data = {
                "status": "ok", 
                "message": "Webhook endpoint working!",
                "method": "GET",
                "bot_token_exists": bool(BOT_TOKEN)
            }
            
            return {
                'statusCode': 200,
                'headers': {
                    'Content-Type': 'application/json',
                },
                'body': json.dumps(response_data)
            }
        
        else:
            return {
                'statusCode': 405,
                'headers': {
                    'Content-Type': 'application/json',
                },
                'body': json.dumps({"error": "Method not allowed"})
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
            'body': json.dumps({"error": error_msg})
        }

# Для совместимости с разными форматами вызовов
def handler_func(event, context=None):
    """Alternative handler name"""
    return handler(event, context)

# Экспортируем обе версии
__all__ = ['handler', 'handler_func'] 