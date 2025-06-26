from http.server import BaseHTTPRequestHandler
import json
import os
import sys
import asyncio
import aiohttp

# Добавляем пути для импорта модулей бота
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

# Конфигурация
BOT_TOKEN = os.getenv('BOT_TOKEN')
MONGODB_URL = os.getenv('MONGODB_URL')

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        
        response_data = {
            "status": "ok",
            "service": "Turan Bot Webhook",
            "version": "2.0",
            "bot_token_configured": bool(BOT_TOKEN),
            "mongodb_configured": bool(MONGODB_URL)
        }
        
        self.wfile.write(json.dumps(response_data).encode('utf-8'))
    
    def do_POST(self):
        try:
            # Читаем тело запроса
            content_length = int(self.headers.get('Content-Length', 0))
            if content_length > 0:
                post_data = self.rfile.read(content_length)
                update_data = json.loads(post_data.decode('utf-8'))
            else:
                update_data = {}
            
            # Обрабатываем update асинхронно
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            try:
                result = loop.run_until_complete(process_telegram_update(update_data))
                
                # Отправляем успешный ответ
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                
                response_data = {
                    "status": "processed",
                    "result": result
                }
                
                self.wfile.write(json.dumps(response_data).encode('utf-8'))
                
            finally:
                loop.close()
            
        except Exception as e:
            # Обработка ошибок
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            
            error_response = {
                "status": "error",
                "message": str(e),
                "type": type(e).__name__
            }
            
            self.wfile.write(json.dumps(error_response).encode('utf-8'))

async def process_telegram_update(update_data):
    """Обрабатывает Telegram update и отправляет ответ"""
    try:
        if not BOT_TOKEN:
            return {"error": "BOT_TOKEN not configured"}
        
        # Извлекаем данные из update
        chat_id = None
        message_text = None
        update_type = "unknown"
        user_id = None
        
        if 'message' in update_data:
            message = update_data['message']
            chat_id = message.get('chat', {}).get('id')
            message_text = message.get('text', '')
            user_id = message.get('from', {}).get('id')
            update_type = "message"
        elif 'callback_query' in update_data:
            callback = update_data['callback_query']
            chat_id = callback.get('message', {}).get('chat', {}).get('id')
            message_text = callback.get('data', '')
            user_id = callback.get('from', {}).get('id')
            update_type = "callback"
        
        if not chat_id:
            return {"error": "No chat_id found"}
        
        # Простая обработка команд
        response_text = ""
        reply_markup = None
        
        if message_text == "/start":
            response_text = """🏪 **Добро пожаловать в Turan Bot!**

🔹 Ваш помощник для заказа товаров
🔹 Быстрый доступ к каталогу
🔹 Удобное оформление заказов

Выберите действие:"""
            
            reply_markup = {
                "inline_keyboard": [
                    [{"text": "📦 Каталог", "callback_data": "menu_catalog"}],
                    [{"text": "🛒 Заказы", "callback_data": "menu_orders"}],
                    [{"text": "📊 Остатки", "callback_data": "menu_stock"}],
                    [{"text": "📈 Аналитика", "callback_data": "menu_analytics"}]
                ]
            }
        
        elif message_text == "menu_catalog" or message_text == "/catalog":
            response_text = """📦 **Каталог товаров**

К сожалению, полная функциональность каталога требует подключения к базе данных.
Для полного функционала запустите бота локально.

Доступные категории:
• Алко 1 (98 товаров)
• Алко 2 (55 товаров) 
• Туран без алко (26 товаров)
• Общее (43 товара)"""
            
            reply_markup = {
                "inline_keyboard": [
                    [{"text": "🔙 Главное меню", "callback_data": "/start"}]
                ]
            }
        
        else:
            response_text = f"""📝 Получено сообщение: "{message_text}"

⚠️ Webhook работает, но для полной функциональности требуется подключение к MongoDB.

Используйте команды:
• /start - главное меню
• /catalog - каталог товаров

🔧 Для полного функционала запустите бота локально."""
        
        # Отправляем ответ через Telegram API
        success = await send_telegram_message(chat_id, response_text, reply_markup, update_type == "callback")
        
        return {
            "chat_id": chat_id,
            "user_id": user_id,
            "message_sent": success,
            "update_type": update_type
        }
        
    except Exception as e:
        return {"error": str(e)}

async def send_telegram_message(chat_id, text, reply_markup=None, is_callback=False):
    """Отправляет сообщение через Telegram API"""
    try:
        if is_callback:
            # Для callback queries используем editMessageText
            url = f"https://api.telegram.org/bot{BOT_TOKEN}/editMessageText"
        else:
            # Для обычных сообщений используем sendMessage
            url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        
        data = {
            "chat_id": chat_id,
            "text": text,
            "parse_mode": "Markdown"
        }
        
        if reply_markup:
            data["reply_markup"] = json.dumps(reply_markup)
        
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=data) as response:
                result = await response.json()
                return result.get('ok', False)
                
    except Exception as e:
        print(f"Error sending message: {e}")
        return False 