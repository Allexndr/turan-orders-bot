import json
import os

# Получаем переменные окружения
BOT_TOKEN = os.getenv('BOT_TOKEN')
MONGODB_URL = os.getenv('MONGODB_URL')

def handler(event, context=None):
    """Simple Vercel handler for Telegram webhook"""
    
    # Получаем HTTP метод
    method = event.get('httpMethod', event.get('method', 'GET'))
    
    # GET запрос - статус
    if method == 'GET':
        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({
                "status": "webhook_active",
                "message": "Telegram bot webhook is running",
                "bot_configured": bool(BOT_TOKEN),
                "method": method
            })
        }
    
    # POST запрос - Telegram update
    if method == 'POST':
        body = event.get('body', '{}')
        
        # Парсим update
        try:
            update = json.loads(body) if isinstance(body, str) else body
            
            # Извлекаем базовую информацию
            chat_id = None
            message_text = None
            
            if 'message' in update:
                chat_id = update['message'].get('chat', {}).get('id')
                message_text = update['message'].get('text')
            elif 'callback_query' in update:
                chat_id = update['callback_query'].get('message', {}).get('chat', {}).get('id')
                message_text = update['callback_query'].get('data')
            
            return {
                'statusCode': 200,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({
                    "status": "update_received",
                    "chat_id": chat_id,
                    "message": message_text,
                    "update_type": "message" if 'message' in update else "callback" if 'callback_query' in update else "unknown"
                })
            }
            
        except Exception as e:
            return {
                'statusCode': 500,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({"error": f"Parse error: {str(e)}"})
            }
    
    # Другие методы
    return {
        'statusCode': 405,
        'headers': {'Content-Type': 'application/json'},
        'body': json.dumps({"error": "Method not allowed"})
    } 