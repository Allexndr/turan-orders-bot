from sqlalchemy import select, func
from sqlalchemy.orm import joinedload

from app.database import autosession
from app.models import Order, OrderItem, Product


async def create_order(user_id: int) -> Order:
    async with autosession() as session:
        order = Order(user_id=user_id)
        session.add(order)
        await session.commit()
        await session.refresh(order)
        return order


async def add_item(order_id, product_id, quantity):
    async with autosession() as session:
        product = await session.get(Product, product_id)
        if not product:
            raise ValueError("Product not found")

        order = await session.get(Order, order_id)
        if not order:
            raise ValueError("Order not found")

        item = OrderItem(order_id=order_id, product_id=product_id, quantity=quantity, price=product.price)
        session.add(item)
        order.total_amount += product.price * quantity
        await session.commit()


async def get_order(order_id):
    async with autosession() as session:
        result = await session.execute(select(Order).options(joinedload(Order.items)).where(Order.id == order_id))
        return result.scalars().first()


async def get_user_orders(user_id: int):
    async with autosession() as session:
        result = await session.execute(
            select(Order)
            .where(Order.user_id == user_id)
            .order_by(Order.created_at.desc())
        )
        return result.scalars().all()


async def get_order_with_items(order_id: int):
    async with autosession() as session:
        result = await session.execute(
            select(Order)
            .options(joinedload(Order.items).joinedload(OrderItem.product))
            .where(Order.id == order_id)
        )
        return result.scalars().first()


async def update_order_status(order_id: int, status: str):
    async with autosession() as session:
        order = await session.get(Order, order_id)
        if order:
            order.status = status
            await session.commit()
            return True
        return False 