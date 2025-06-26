from typing import List, Optional
from bson import ObjectId
from app.models import Product


async def get_products(skip: int = 0, limit: int = 100) -> List[Product]:
    """Получение списка продуктов"""
    return await Product.find().skip(skip).limit(limit).to_list()


async def get_product_by_id(product_id: str) -> Optional[Product]:
    """Получение продукта по ID"""
    try:
        return await Product.get(ObjectId(product_id))
    except Exception:
        return None


async def create_product(name: str, package: str, price: float) -> Product:
    """Создание нового продукта"""
    product = Product(
        name=name,
        package=package,
        price=price
    )
    await product.insert()
    return product


async def update_product(product_id: str, name: str = None, package: str = None, price: float = None) -> Optional[Product]:
    """Обновление продукта"""
    try:
        product = await Product.get(ObjectId(product_id))
        if not product:
            return None
    except Exception:
        return None
    
    if name is not None:
        product.name = name
    if package is not None:
        product.package = package
    if price is not None:
        product.price = price
    
    await product.save()
    return product


async def delete_product(product_id: str) -> bool:
    """Удаление продукта"""
    try:
        product = await Product.get(ObjectId(product_id))
        if product:
            await product.delete()
            return True
    except Exception:
        pass
    return False


async def search_products(query: str) -> List[Product]:
    """Поиск продуктов по названию"""
    return await Product.find({"name": {"$regex": query, "$options": "i"}}).to_list()


async def get_products_count() -> int:
    """Получение общего количества продуктов"""
    return await Product.count()


async def get_products_by_category(category: str, skip: int = 0, limit: int = 20) -> List[Product]:
    """Получить товары по категории с пагинацией"""
    # Добавляем фильтр по цене больше 0 и по категории
    if category == "Общее":
        # Для категории "Общее" ищем товары с category = None или "Общее"
        return await Product.find(
            {"$or": [{"category": None}, {"category": "Общее"}]},
            Product.price > 0
        ).skip(skip).limit(limit).to_list()
    else:
        return await Product.find(
            Product.category == category,
            Product.price > 0
        ).skip(skip).limit(limit).to_list()


async def get_categories_stats() -> dict:
    """Получить статистику по категориям"""
    # Получаем только товары с ценой больше 0
    products = await Product.find(Product.price > 0).to_list()
    categories_stats = {}
    
    for product in products:
        category = getattr(product, 'category', 'Общее')
        categories_stats[category] = categories_stats.get(category, 0) + 1
    
    # Сортируем категории в нужном порядке
    ordered_categories = {}
    for category in ["Алко 1", "Алко 2", "Туран без алко", "Общее"]:
        if category in categories_stats:
            ordered_categories[category] = categories_stats[category]
    
    # Добавляем остальные категории
    for category, count in categories_stats.items():
        if category not in ordered_categories:
            ordered_categories[category] = count
    
    return ordered_categories


async def get_category_products_count(category: str) -> int:
    """Получить количество товаров в категории"""
    if category == "Общее":
        # Для категории "Общее" считаем товары с category = None или "Общее"
        return await Product.find(
            {"$or": [{"category": None}, {"category": "Общее"}]},
            Product.price > 0
        ).count()
    else:
        return await Product.find(
            Product.category == category,
            Product.price > 0
        ).count() 