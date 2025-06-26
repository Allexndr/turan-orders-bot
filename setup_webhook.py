import asyncio
import aiohttp
from app.config import settings

async def setup_webhook():
    """Настройка веб-хука для Telegram бота"""
    
    # URL вашего Vercel деплоя (замените на реальный)
    WEBHOOK_URL = "https://your-vercel-app.vercel.app/api/webhook"
    
    url = f"https://api.telegram.org/bot{settings.bot_token}/setWebhook"
    
    data = {
        "url": WEBHOOK_URL,
        "drop_pending_updates": True
    }
    
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=data) as response:
            result = await response.json()
            print(f"Webhook setup result: {result}")
            
            if result.get("ok"):
                print("✅ Webhook успешно настроен!")
                print(f"📡 URL: {WEBHOOK_URL}")
            else:
                print("❌ Ошибка настройки webhook:")
                print(result.get("description", "Unknown error"))

if __name__ == "__main__":
    asyncio.run(setup_webhook()) 