from typing import Dict, Any
from app.models import Order, Product, Stock, User, OrderItem
from datetime import datetime, timedelta


async def get_analytics_data() -> Dict[str, Any]:
    """Получение аналитических данных"""
    # Получаем все данные
    orders = await Order.find().to_list()
    products = await Product.find().to_list()
    stocks = await Stock.find().to_list()
    users = await User.find().to_list()
    
    # Подсчитываем основные метрики
    total_orders = len(orders)
    total_products = len(products)
    total_users = len(users)
    
    # Подсчитываем общую сумму заказов
    total_revenue = 0
    for order in orders:
        if hasattr(order, 'items') and order.items:
            for item in order.items:
                if hasattr(item, 'total_price'):
                    total_revenue += item.total_price
                elif hasattr(item, 'price') and hasattr(item, 'quantity'):
                    total_revenue += item.price * item.quantity
    
    # Подсчитываем общий остаток товаров
    total_stock = 0
    for stock in stocks:
        total_stock += stock.quantity
    
    # Подсчитываем статистику по категориям товаров
    categories_stats = {}
    for product in products:
        category = getattr(product, 'category', 'Общее')
        categories_stats[category] = categories_stats.get(category, 0) + 1
    
    # Анализ по дням (последние 7 дней)
    today = datetime.utcnow().date()
    daily_stats = {}
    
    for i in range(7):
        date = today - timedelta(days=i)
        daily_orders = [o for o in orders if o.created_at.date() == date]
        daily_revenue = 0
        
        for order in daily_orders:
            if hasattr(order, 'items') and order.items:
                for item in order.items:
                    if hasattr(item, 'total_price'):
                        daily_revenue += item.total_price
                    elif hasattr(item, 'price') and hasattr(item, 'quantity'):
                        daily_revenue += item.price * item.quantity
        
        daily_stats[date.strftime("%Y-%m-%d")] = {
            "orders": len(daily_orders),
            "revenue": daily_revenue
        }
    
    return {
        "total_orders": total_orders,
        "total_products": total_products,
        "total_users": total_users,
        "total_revenue": total_revenue,
        "total_stock": total_stock,
        "categories_stats": categories_stats,
        "daily_stats": daily_stats
    }


async def get_total_orders_sum() -> float:
    """Получить общую сумму всех заказов"""
    orders = await Order.find().to_list()
    total_sum = 0
    
    for order in orders:
        if hasattr(order, 'items') and order.items:
            for item in order.items:
                if hasattr(item, 'total_price'):
                    total_sum += item.total_price
                elif hasattr(item, 'price') and hasattr(item, 'quantity'):
                    total_sum += item.price * item.quantity
    
    return total_sum 