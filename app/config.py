import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()


@dataclass
class Settings:
    # Telegram Bot
    bot_token: str = os.getenv("BOT_TOKEN", "7665066386:AAHSzFTptehCoWQhdxRSysjEc_bjQ1u8Lkw")
    
    # MongoDB Atlas
    mongodb_url: str = os.getenv("MONGODB_URL", "mongodb+srv://alxndrmurdasov:X54WECTTV8eHFoMT@cluster0.gxvexo3.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
    database_name: str = os.getenv("DATABASE_NAME", "turan")


settings = Settings() 