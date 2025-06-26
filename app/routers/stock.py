from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

from app.services import stock as stock_service, auth as auth_service, catalog as catalog_service

router = Router(name="stock")


class StockStates(StatesGroup):
    waiting_quantity = State()


async def show_stock_menu(callback: types.CallbackQuery, page: int = 0):
    user = await auth_service.get_logged_in_user(callback.from_user.id)
    if not user:
        await callback.answer("❌ Пользователь не найден!")
        return

    # Получаем все товары и их остатки
    products = await catalog_service.get_products()
    stocks = await stock_service.get_user_stocks(str(user.id))
    
    # Создаем словарь остатков по product_id
    stock_dict = {str(stock_data["stock"].product_id): stock_data["stock"].quantity for stock_data in stocks}
    
    if not products:
        text = "📊 <b>Управление остатками</b>\n\n❌ Товары не найдены."
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔙 Назад в меню", callback_data="back_to_menu")]
        ])
        await callback.message.edit_text(text, reply_markup=keyboard)
        await callback.answer()
        return
    
    # Пагинация - показываем по 20 товаров на странице
    items_per_page = 20
    total_pages = (len(products) + items_per_page - 1) // items_per_page
    start_idx = page * items_per_page
    end_idx = min(start_idx + items_per_page, len(products))
    page_products = products[start_idx:end_idx]
    
    text = "📊 <b>Управление остатками</b>\n\n"
    text += f"📦 Всего товаров: {len(products)}\n"
    text += f"📄 Страница {page + 1} из {total_pages}\n"
    text += f"Показано: {start_idx + 1}-{end_idx} из {len(products)}\n\n"
    text += "Выберите товар для изменения остатка:\n\n"
    
    keyboard_buttons = []
    
    # Группируем товары по 2 в ряд для кнопок
    for i in range(0, len(page_products), 2):
        row = []
        
        # Первый товар в ряду
        product1 = page_products[i]
        current_stock1 = stock_dict.get(str(product1.id), 0)
        short_name1 = product1.name[:15] + "..." if len(product1.name) > 15 else product1.name
        row.append(InlineKeyboardButton(
            text=f"📝 {short_name1} ({current_stock1})",
            callback_data=f"edit_stock_{str(product1.id)}"
        ))
        
        # Второй товар в ряду (если есть)
        if i + 1 < len(page_products):
            product2 = page_products[i + 1]
            current_stock2 = stock_dict.get(str(product2.id), 0)
            short_name2 = product2.name[:15] + "..." if len(product2.name) > 15 else product2.name
            row.append(InlineKeyboardButton(
                text=f"📝 {short_name2} ({current_stock2})",
                callback_data=f"edit_stock_{str(product2.id)}"
            ))
        
        keyboard_buttons.append(row)
    
    # Добавляем кнопки навигации по страницам
    nav_buttons = []
    if page > 0:
        nav_buttons.append(InlineKeyboardButton(text="⬅️ Назад", callback_data=f"stock_page_{page-1}"))
    if page < total_pages - 1:
        nav_buttons.append(InlineKeyboardButton(text="➡️ Далее", callback_data=f"stock_page_{page+1}"))
    
    if nav_buttons:
        keyboard_buttons.append(nav_buttons)
    
    keyboard_buttons.append([
        InlineKeyboardButton(text="🔙 Назад в меню", callback_data="back_to_menu")
    ])
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)
    
    await callback.message.edit_text(text, reply_markup=keyboard)
    await callback.answer()


@router.callback_query(F.data.startswith("stock_page_"))
async def stock_page(callback: types.CallbackQuery):
    page = int(callback.data.split("_")[-1])
    await show_stock_menu(callback, page)


@router.callback_query(F.data.startswith("edit_stock_"))
async def edit_stock(callback: types.CallbackQuery, state: FSMContext):
    product_id = callback.data.split("_")[-1]
    
    # Получаем информацию о товаре
    products = await catalog_service.get_products()
    product = next((p for p in products if str(p.id) == product_id), None)
    
    if not product:
        await callback.answer("❌ Товар не найден!")
        return
    
    # Получаем текущий остаток
    user = await auth_service.get_logged_in_user(callback.from_user.id)
    current_stock = await stock_service.get_stock(str(user.id), product_id)
    current_qty = current_stock.quantity if current_stock else 0
    
    # Быстрые кнопки для изменения остатка
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="0️⃣", callback_data=f"set_stock_{product_id}_0"),
            InlineKeyboardButton(text="1️⃣0️⃣", callback_data=f"set_stock_{product_id}_10"),
            InlineKeyboardButton(text="2️⃣0️⃣", callback_data=f"set_stock_{product_id}_20")
        ],
        [
            InlineKeyboardButton(text="5️⃣0️⃣", callback_data=f"set_stock_{product_id}_50"),
            InlineKeyboardButton(text="💯", callback_data=f"set_stock_{product_id}_100"),
            InlineKeyboardButton(text="2️⃣0️⃣0️⃣", callback_data=f"set_stock_{product_id}_200")
        ],
        [
            InlineKeyboardButton(text="✏️ Ввести вручную", callback_data=f"manual_stock_{product_id}")
        ],
        [
            InlineKeyboardButton(text="🔙 К остаткам", callback_data="menu_stock")
        ]
    ])
    
    await callback.message.edit_text(
        f"📊 <b>Изменение остатка</b>\n\n"
        f"📦 <b>{product.name}</b>\n"
        f"📋 Упаковка: {product.package}\n"
        f"📊 Текущий остаток: <b>{current_qty}</b>\n\n"
        f"Выберите новое количество:",
        reply_markup=keyboard
    )
    await callback.answer()


@router.callback_query(F.data.startswith("set_stock_"))
async def set_stock(callback: types.CallbackQuery):
    parts = callback.data.split("_")
    product_id = parts[2]
    quantity = int(parts[3])
    
    user = await auth_service.get_logged_in_user(callback.from_user.id)
    if not user:
        await callback.answer("❌ Пользователь не найден!")
        return
    
    await stock_service.update_stock(str(user.id), product_id, quantity)
    
    # Получаем название товара
    products = await catalog_service.get_products()
    product = next((p for p in products if str(p.id) == product_id), None)
    product_name = product.name if product else f"Товар #{product_id}"
    
    await callback.answer(f"✅ Остаток {product_name} установлен: {quantity}")
    
    # Возвращаемся к редактированию этого товара
    await edit_stock(callback, None)


@router.callback_query(F.data.startswith("manual_stock_"))
async def manual_stock(callback: types.CallbackQuery, state: FSMContext):
    product_id = callback.data.split("_")[-1]
    
    # Получаем информацию о товаре
    products = await catalog_service.get_products()
    product = next((p for p in products if str(p.id) == product_id), None)
    
    if not product:
        await callback.answer("❌ Товар не найден!")
        return
    
    await state.update_data(product_id=product_id)
    await state.set_state(StockStates.waiting_quantity)
    
    await callback.message.edit_text(
        f"✏️ <b>Ручной ввод остатка</b>\n\n"
        f"📦 <b>{product.name}</b>\n"
        f"📋 {product.package}\n\n"
        f"Введите количество (только цифры):",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="❌ Отмена", callback_data=f"edit_stock_{product_id}")]
        ])
    )
    await callback.answer()


@router.message(StockStates.waiting_quantity)
async def process_manual_quantity(msg: types.Message, state: FSMContext):
    try:
        quantity = int(msg.text.strip())
        if quantity < 0:
            await msg.answer("❌ Количество не может быть отрицательным. Попробуйте еще раз:")
            return
    except ValueError:
        await msg.answer("❌ Введите корректное число. Попробуйте еще раз:")
        return
    
    data = await state.get_data()
    product_id = data["product_id"]
    
    user = await auth_service.get_logged_in_user(msg.from_user.id)
    if not user:
        await msg.answer("❌ Пользователь не найден!")
        await state.clear()
        return
    
    await stock_service.update_stock(str(user.id), product_id, quantity)
    
    # Получаем название товара
    products = await catalog_service.get_products()
    product = next((p for p in products if str(p.id) == product_id), None)
    product_name = product.name if product else f"Товар #{product_id}"
    
    await msg.answer(
        f"✅ <b>Остаток обновлен!</b>\n\n"
        f"📦 {product_name}\n"
        f"📊 Новый остаток: <b>{quantity}</b>",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="📊 К остаткам", callback_data="menu_stock")],
            [InlineKeyboardButton(text="🏠 Главное меню", callback_data="back_to_menu")]
        ])
    )
    
    await state.clear()


@router.message(Command("stock"))
async def cmd_stock(msg: types.Message):
    fake_callback = types.CallbackQuery(
        id="fake",
        from_user=msg.from_user,
        chat_instance="fake",
        message=msg,
        data="menu_stock"
    )
    await show_stock_menu(fake_callback) 