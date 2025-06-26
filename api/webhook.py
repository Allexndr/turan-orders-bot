import json
import os

# Инициализация переменных окружения
BOT_TOKEN = os.getenv('BOT_TOKEN')

def handler(event, context=None):
    """Simple Vercel handler function"""
    return {
        'statusCode': 200,
        'headers': {'Content-Type': 'application/json'},
        'body': json.dumps({
            "status": "ok", 
            "message": "Webhook working!",
            "bot_token_exists": bool(BOT_TOKEN)
        })
    }

# Для совместимости с разными форматами вызовов
def handler_func(event, context=None):
    """Alternative handler name"""
    return handler(event, context)

# Экспортируем обе версии
__all__ = ['handler', 'handler_func'] 