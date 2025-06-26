from datetime import datetime
from typing import Optional, List
from beanie import Document
from pydantic import BaseModel


class User(Document):
    telegram_id: Optional[int] = None
    username: str
    password_hash: str
    created_at: datetime = datetime.utcnow()
    is_active: bool = True
    is_logged_in: bool = False  # Для отслеживания активной сессии
    
    class Settings:
        name = "users"


class Product(Document):
    name: str
    package: str
    price: float
    category: str = "Общее"  # Категория товара
    created_at: datetime = datetime.utcnow()
    
    class Settings:
        name = "products"


class Stock(Document):
    product_id: str  # Beanie использует строковые ObjectId
    user_id: str
    quantity: int = 0
    updated_at: datetime = datetime.utcnow()
    
    class Settings:
        name = "stock"


class Order(Document):
    user_id: str
    status: str = "pending"  # pending, confirmed, cancelled
    total_amount: float = 0.0
    created_at: datetime = datetime.utcnow()
    updated_at: datetime = datetime.utcnow()
    
    class Settings:
        name = "orders"


class OrderItem(Document):
    order_id: str
    product_id: str
    quantity: int
    price: float
    
    class Settings:
        name = "order_items"


# Pydantic модели для запросов
class UserCreate(BaseModel):
    username: str
    password: str


class ProductCreate(BaseModel):
    name: str
    package: str
    price: float


class OrderCreate(BaseModel):
    user_id: str
    items: List[dict] 