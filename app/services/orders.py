from typing import List, Optional
from datetime import datetime
from bson import ObjectId
from app.models import Order, OrderItem, Product


async def create_order(user_id: str) -> Order:
    """Создание нового заказа"""
    order = Order(user_id=user_id)
    await order.insert()
    return order


async def add_item_to_order(order_id: str, product_id: str, quantity: int) -> OrderItem:
    """Добавление товара в заказ"""
    # Получаем продукт для цены
    try:
        product = await Product.get(ObjectId(product_id))
        if not product:
            raise ValueError("Продукт не найден")
    except Exception:
        raise ValueError("Продукт не найден")
    
    # Проверяем, есть ли уже такой товар в заказе
    existing_item = await OrderItem.find_one(
        OrderItem.order_id == order_id,
        OrderItem.product_id == product_id
    )
    
    if existing_item:
        # Обновляем количество
        existing_item.quantity += quantity
        await existing_item.save()
        return existing_item
    else:
        # Создаем новый элемент заказа
        order_item = OrderItem(
            order_id=order_id,
            product_id=product_id,
            quantity=quantity,
            price=product.price
        )
        await order_item.insert()
        return order_item


async def get_user_orders(user_id: str) -> List[Order]:
    """Получение заказов пользователя"""
    return await Order.find(Order.user_id == user_id).sort(-Order.created_at).to_list()


async def get_order_by_id(order_id: str) -> Optional[Order]:
    """Получение заказа по ID"""
    try:
        return await Order.get(ObjectId(order_id))
    except Exception:
        return None


async def get_order_items(order_id: str) -> List[OrderItem]:
    """Получение элементов заказа"""
    return await OrderItem.find(OrderItem.order_id == order_id).to_list()


async def get_order_with_items(order_id: str) -> Optional[dict]:
    """Получение заказа с элементами и продуктами"""
    try:
        order = await Order.get(ObjectId(order_id))
        if not order:
            return None
    except Exception:
        return None
    
    items = await OrderItem.find(OrderItem.order_id == order_id).to_list()
    
    # Получаем информацию о продуктах
    order_data = {
        "order": order,
        "items": []
    }
    
    total_amount = 0
    for item in items:
        try:
            product = await Product.get(ObjectId(item.product_id))
            if product:
                item_total = item.quantity * item.price
                total_amount += item_total
                order_data["items"].append({
                    "item": item,
                    "product": product,
                    "total": item_total
                })
        except Exception:
            continue
    
    order_data["total_amount"] = total_amount
    return order_data


async def update_order_status(order_id: str, status: str) -> Optional[Order]:
    """Обновление статуса заказа"""
    try:
        order = await Order.get(ObjectId(order_id))
        if order:
            order.status = status
            order.updated_at = datetime.utcnow()
            await order.save()
        return order
    except Exception:
        return None


async def calculate_order_total(order_id: str) -> float:
    """Расчет общей суммы заказа"""
    items = await OrderItem.find(OrderItem.order_id == order_id).to_list()
    total = sum(item.quantity * item.price for item in items)
    
    # Обновляем сумму в заказе
    try:
        order = await Order.get(ObjectId(order_id))
        if order:
            order.total_amount = total
            await order.save()
    except Exception:
        pass
    
    return total


async def remove_item_from_order(order_id: str, product_id: str) -> bool:
    """Удаление товара из заказа"""
    item = await OrderItem.find_one(
        OrderItem.order_id == order_id,
        OrderItem.product_id == product_id
    )
    if item:
        await item.delete()
        return True
    return False


async def clear_order(order_id: str) -> bool:
    """Очистка заказа"""
    items = await OrderItem.find(OrderItem.order_id == order_id).to_list()
    for item in items:
        await item.delete()
    return True 