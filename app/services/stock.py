from typing import List, Optional
from datetime import datetime
from bson import ObjectId
from app.models import Stock, Product


async def get_user_stocks(user_id: str) -> List[dict]:
    """Получение остатков пользователя с информацией о продуктах"""
    stocks = await Stock.find(Stock.user_id == user_id).to_list()
    
    result = []
    for stock in stocks:
        try:
            product = await Product.get(ObjectId(stock.product_id))
            if product:
                result.append({
                    "stock": stock,
                    "product": product
                })
        except Exception:
            continue
    
    return result


async def get_stock(user_id: str, product_id: str) -> Optional[Stock]:
    """Получение остатка конкретного товара у пользователя"""
    return await Stock.find_one(
        Stock.user_id == user_id,
        Stock.product_id == product_id
    )


async def update_stock(user_id: str, product_id: str, quantity: int) -> Stock:
    """Обновление остатка товара"""
    stock = await get_stock(user_id, product_id)
    
    if stock:
        stock.quantity = quantity
        stock.updated_at = datetime.utcnow()
        await stock.save()
    else:
        stock = Stock(
            user_id=user_id,
            product_id=product_id,
            quantity=quantity
        )
        await stock.insert()
    
    return stock


async def add_to_stock(user_id: str, product_id: str, quantity: int) -> Stock:
    """Добавление к остатку товара"""
    stock = await get_stock(user_id, product_id)
    
    if stock:
        stock.quantity += quantity
        stock.updated_at = datetime.utcnow()
        await stock.save()
    else:
        stock = Stock(
            user_id=user_id,
            product_id=product_id,
            quantity=quantity
        )
        await stock.insert()
    
    return stock


async def reduce_stock(user_id: str, product_id: str, quantity: int) -> Optional[Stock]:
    """Уменьшение остатка товара"""
    stock = await get_stock(user_id, product_id)
    
    if not stock:
        return None
    
    if stock.quantity < quantity:
        raise ValueError("Недостаточно товара на складе")
    
    stock.quantity -= quantity
    stock.updated_at = datetime.utcnow()
    await stock.save()
    
    return stock


async def get_low_stock_items(user_id: str, threshold: int = 10) -> List[dict]:
    """Получение товаров с низким остатком"""
    stocks = await Stock.find(
        Stock.user_id == user_id,
        Stock.quantity <= threshold
    ).to_list()
    
    result = []
    for stock in stocks:
        try:
            product = await Product.get(ObjectId(stock.product_id))
            if product:
                result.append({
                    "stock": stock,
                    "product": product
                })
        except Exception:
            continue
    
    return result


async def get_total_stock_value(user_id: str) -> float:
    """Расчет общей стоимости остатков пользователя"""
    stocks = await Stock.find(Stock.user_id == user_id).to_list()
    
    total_value = 0
    for stock in stocks:
        try:
            product = await Product.get(ObjectId(stock.product_id))
            if product:
                total_value += stock.quantity * product.price
        except Exception:
            continue
    
    return total_value


async def create_stock_for_all_products(user_id: str, default_quantity: int = 0) -> List[Stock]:
    """Создание записей остатков для всех продуктов пользователя"""
    products = await Product.find().to_list()
    stocks = []
    
    for product in products:
        existing_stock = await get_stock(user_id, str(product.id))
        if not existing_stock:
            stock = Stock(
                user_id=user_id,
                product_id=str(product.id),
                quantity=default_quantity
            )
            await stock.insert()
            stocks.append(stock)
    
    return stocks 