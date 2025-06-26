from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from app.services import orders as order_service, auth as auth_service

router = Router(name="order")


async def show_orders_menu(callback: types.CallbackQuery):
    user = await auth_service.get_logged_in_user(callback.from_user.id)
    if not user:
        await callback.answer("❌ Пользователь не найден!")
        return

    # Получаем заказы пользователя
    orders = await order_service.get_user_orders(str(user.id))
    
    if not orders:
        await callback.message.edit_text(
            "🛒 <b>Мои заказы</b>\n\n"
            "📭 У вас пока нет заказов.\n"
            "Создайте первый заказ через каталог товаров!",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="📦 Каталог товаров", callback_data="menu_catalog")],
                [InlineKeyboardButton(text="🔙 Назад в меню", callback_data="back_to_menu")]
            ])
        )
        await callback.answer()
        return

    # Подсчитываем общую сумму всех заказов
    total_sum = sum(order.total_amount for order in orders)
    
    text = "🛒 <b>Мои заказы</b>\n\n"
    text += f"📊 Всего заказов: {len(orders)}\n\n"
    
    keyboard_buttons = []
    
    for order in orders:
        status_emoji = {
            "draft": "📝",
            "confirmed": "✅", 
            "paid": "💳",
            "canceled": "❌"
        }.get(order.status, "❓")
        
        text += f"{status_emoji} <b>Заказ #{str(order.id)}</b>\n"
        text += f"💰 Сумма: {order.total_amount:.2f} ₸\n"
        text += f"📅 {order.created_at.strftime('%d.%m.%Y %H:%M')}\n\n"
    
    # Группируем заказы по 2 в ряд для кнопок
    for i in range(0, len(orders), 2):
        row = []
        
        # Первый заказ в ряду
        order1 = orders[i]
        row.append(InlineKeyboardButton(
            text=f"👁 #{str(order1.id)} - {order1.total_amount:.0f}₸",
            callback_data=f"view_order_{str(order1.id)}"
        ))
        
        # Второй заказ в ряду (если есть)
        if i + 1 < len(orders):
            order2 = orders[i + 1]
            row.append(InlineKeyboardButton(
                text=f"👁 #{str(order2.id)} - {order2.total_amount:.0f}₸",
                callback_data=f"view_order_{str(order2.id)}"
            ))
        
        keyboard_buttons.append(row)
    
    # Добавляем общую сумму в конец
    text += f"💳 <b>Общая сумма всех заказов: {total_sum:.2f} ₸</b>"
    
    keyboard_buttons.append([
        InlineKeyboardButton(text="➕ Новый заказ", callback_data="menu_catalog"),
        InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_menu")
    ])
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)
    
    await callback.message.edit_text(text, reply_markup=keyboard)
    await callback.answer()


@router.callback_query(F.data.startswith("view_order_"))
async def view_order(callback: types.CallbackQuery):
    order_id = callback.data.split("_")[-1]
    
    order_data = await order_service.get_order_with_items(order_id)
    if not order_data:
        await callback.answer("❌ Заказ не найден!")
        return
    
    order = order_data["order"]
    
    status_emoji = {
        "draft": "📝",
        "confirmed": "✅", 
        "paid": "💳",
        "canceled": "❌"
    }.get(order.status, "❓")
    
    text = f"🛒 <b>Заказ #{str(order.id)}</b>\n\n"
    text += f"📊 Статус: {status_emoji} {order.status}\n"
    text += f"📅 Создан: {order.created_at.strftime('%d.%m.%Y %H:%M')}\n\n"
    
    if order_data["items"]:
        text += "<b>📦 Состав заказа:</b>\n"
        for item_data in order_data["items"]:
            item = item_data["item"]
            product = item_data["product"]
            text += f"• {product.name}\n"
            text += f"  {item.quantity} × {item.price:.2f} ₸ = {item_data['total']:.2f} ₸\n"
        text += f"\n💰 <b>Итого: {order_data['total_amount']:.2f} ₸</b>"
    else:
        text += "📭 Заказ пуст"
    
    keyboard_buttons = []
    
    if order.status == "draft":
        keyboard_buttons.append([
            InlineKeyboardButton(text="✅ Подтвердить", callback_data=f"confirm_order_{str(order.id)}"),
            InlineKeyboardButton(text="❌ Отменить", callback_data=f"cancel_order_{str(order.id)}")
        ])
    
    keyboard_buttons.append([
        InlineKeyboardButton(text="🔙 К заказам", callback_data="menu_orders")
    ])
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)
    
    await callback.message.edit_text(text, reply_markup=keyboard)
    await callback.answer()


@router.callback_query(F.data.startswith("confirm_order_"))
async def confirm_order(callback: types.CallbackQuery):
    order_id = callback.data.split("_")[-1]
    
    success = await order_service.update_order_status(order_id, "confirmed")
    if success:
        await callback.answer("✅ Заказ подтвержден!")
        await view_order(callback)  # Обновляем отображение
    else:
        await callback.answer("❌ Ошибка при подтверждении заказа!")


@router.callback_query(F.data.startswith("cancel_order_"))
async def cancel_order(callback: types.CallbackQuery):
    order_id = callback.data.split("_")[-1]
    
    success = await order_service.update_order_status(order_id, "canceled")
    if success:
        await callback.answer("❌ Заказ отменен!")
        await view_order(callback)  # Обновляем отображение
    else:
        await callback.answer("❌ Ошибка при отмене заказа!")


@router.message(Command("order"))
async def cmd_order(msg: types.Message):
    # Перенаправляем в меню заказов
    fake_callback = types.CallbackQuery(
        id="fake",
        from_user=msg.from_user,
        chat_instance="fake",
        message=msg,
        data="menu_orders"
    )
    await show_orders_menu(fake_callback) 