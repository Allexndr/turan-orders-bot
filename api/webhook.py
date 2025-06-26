from http.server import BaseHTTPRequestHandler
import json
import os

# Получаем переменные окружения
BOT_TOKEN = os.getenv('BOT_TOKEN')
MONGODB_URL = os.getenv('MONGODB_URL')

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        
        response = {
            "status": "webhook_active",
            "message": "Telegram bot webhook running on Vercel",
            "bot_configured": bool(os.getenv('BOT_TOKEN'))
        }
        
        self.wfile.write(json.dumps(response).encode())
    
    def do_POST(self):
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            
            # Парсим JSON
            update = json.loads(post_data.decode('utf-8'))
            
            # Извлекаем данные
            chat_id = None
            message_text = None
            
            if 'message' in update:
                chat_id = update['message'].get('chat', {}).get('id')
                message_text = update['message'].get('text')
            elif 'callback_query' in update:
                chat_id = update['callback_query'].get('message', {}).get('chat', {}).get('id')
                message_text = update['callback_query'].get('data')
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            
            response = {
                "status": "update_received",
                "chat_id": chat_id,
                "message": message_text,
                "update_type": "message" if 'message' in update else "callback" if 'callback_query' in update else "unknown"
            }
            
            self.wfile.write(json.dumps(response).encode())
            
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            
            error_response = {"error": str(e)}
            self.wfile.write(json.dumps(error_response).encode()) 