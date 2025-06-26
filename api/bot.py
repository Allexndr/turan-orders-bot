from http.server import BaseHTTPRequestHandler
import json
import os

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        
        response_data = {
            "status": "ok",
            "service": "Turan Bot Webhook",
            "version": "1.0",
            "bot_token_configured": bool(os.getenv('BOT_TOKEN')),
            "mongodb_configured": bool(os.getenv('MONGODB_URL'))
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
            
            # Простая обработка для демонстрации
            chat_id = None
            message_text = None
            update_type = "unknown"
            
            if 'message' in update_data:
                message = update_data['message']
                chat_id = message.get('chat', {}).get('id')
                message_text = message.get('text', '')
                update_type = "message"
            elif 'callback_query' in update_data:
                callback = update_data['callback_query']
                chat_id = callback.get('message', {}).get('chat', {}).get('id')
                message_text = callback.get('data', '')
                update_type = "callback"
            
            # Отправляем успешный ответ
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            
            response_data = {
                "status": "received",
                "update_type": update_type,
                "chat_id": chat_id,
                "message_text": message_text,
                "timestamp": str(update_data.get('update_id', 'unknown'))
            }
            
            self.wfile.write(json.dumps(response_data).encode('utf-8'))
            
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