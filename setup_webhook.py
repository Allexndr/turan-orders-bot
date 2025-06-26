import requests
import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv('BOT_TOKEN')
WEBHOOK_URL = 'https://turan-bot.vercel.app/api/webhook'

def setup_webhook():
    url = f'https://api.telegram.org/bot{BOT_TOKEN}/setWebhook'
    data = {'url': WEBHOOK_URL}
    
    response = requests.post(url, data=data)
    result = response.json()
    
    print(f"Webhook setup result: {result}")
    
    if result.get('ok'):
        print("✅ Webhook успешно настроен!")
        print(f"📡 URL: {WEBHOOK_URL}")
    else:
        print("❌ Ошибка настройки webhook:")
        print(result.get('description', 'Неизвестная ошибка'))

if __name__ == "__main__":
    if not BOT_TOKEN:
        print("❌ BOT_TOKEN не найден в .env файле")
    else:
        setup_webhook() 