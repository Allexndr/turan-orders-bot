import json
import os

# Инициализация переменных окружения
BOT_TOKEN = os.getenv('BOT_TOKEN')

def handler(event, context=None):
    """Simple Vercel handler function"""
    try:
        # Возвращаем простой ответ для любого запроса
        response_data = {
            "status": "ok", 
            "message": "Simple webhook working!",
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
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
            },
            'body': json.dumps({"error": str(e)})
        }

# Для совместимости с разными форматами вызовов
def handler_func(event, context=None):
    """Alternative handler name"""
    return handler(event, context)

# Экспортируем обе версии
__all__ = ['handler', 'handler_func'] 