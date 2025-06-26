import asyncio
import json
import os

# Инициализация переменных окружения
BOT_TOKEN = os.getenv('BOT_TOKEN')
MONGODB_URL = os.getenv('MONGODB_URL', 'mongodb://localhost:27017')
DATABASE_NAME = os.getenv('DATABASE_NAME', 'turan_bot')

def handler(request):
    """Простой обработчик для тестирования"""
    try:
        print(f"Handler called with BOT_TOKEN: {'***' if BOT_TOKEN else 'None'}")
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                "status": "ok", 
                "message": "Webhook working!",
                "bot_token_exists": bool(BOT_TOKEN)
            })
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