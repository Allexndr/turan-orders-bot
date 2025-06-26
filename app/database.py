from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from app.config import settings
from app.models import User, Product, Stock, Order, OrderItem


class Database:
    client: AsyncIOMotorClient = None
    database = None


db = Database()


async def connect_to_mongo():
    """Подключение к MongoDB"""
    db.client = AsyncIOMotorClient(settings.mongodb_url)
    db.database = db.client[settings.database_name]
    
    # Инициализация Beanie
    await init_beanie(
        database=db.database,
        document_models=[User, Product, Stock, Order, OrderItem]
    )
    print("Connected to MongoDB")


async def close_mongo_connection():
    """Закрытие подключения к MongoDB"""
    if db.client:
        db.client.close()
        print("Disconnected from MongoDB")


async def get_database():
    """Получение экземпляра базы данных"""
    return db.database 