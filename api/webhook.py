import asyncio
import json
import os
from http.server import BaseHTTPRequestHandler

# Инициализация переменных окружения
BOT_TOKEN = os.getenv('BOT_TOKEN')
MONGODB_URL = os.getenv('MONGODB_URL', 'mongodb://localhost:27017')
DATABASE_NAME = os.getenv('DATABASE_NAME', 'turan_bot')

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        """Обработка POST запросов от Telegram"""
        try:
            print(f"Handler called with BOT_TOKEN: {'***' if BOT_TOKEN else 'None'}")
            
            # Отправляем ответ
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            
            response = {
                "status": "ok", 
                "message": "Webhook working!",
                "bot_token_exists": bool(BOT_TOKEN)
            }
            
            self.wfile.write(json.dumps(response).encode('utf-8'))
            
        except Exception as e:
            error_msg = f"Handler error: {str(e)}"
            print(error_msg)
            
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            
            error_response = {"error": error_msg}
            self.wfile.write(json.dumps(error_response).encode('utf-8'))
    
    def do_GET(self):
        """Обработка GET запросов для тестирования"""
        try:
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            
            response = {
                "status": "ok", 
                "message": "Webhook endpoint working!",
                "method": "GET"
            }
            
            self.wfile.write(json.dumps(response).encode('utf-8'))
            
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            
            error_response = {"error": str(e)}
            self.wfile.write(json.dumps(error_response).encode('utf-8')) 