from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from app.services import catalog as catalog_service
from app.services.auth import get_logged_in_user

router = Router(name="catalog")


def truncate_text(text: str, max_length: int) -> str:
    """Сокращает текст до указанной длины"""
    if len(text) <= max_length:
        return text
    return text[:max_length-3] + "..."


@router.callback_query(F.data == "menu_catalog")
async def catalog_handler(callback: types.CallbackQuery):
    """Обработчик каталога товаров - показ категорий"""
    user = await get_logged_in_user(callback.from_user.id)
    if not user:
        await callback.message.edit_text("❌ Вы не авторизованы. Используйте /start для входа.")
        return
    
    # Получаем статистику по категориям
    categories_stats = await catalog_service.get_categories_stats()
    
    # Создаем клавиатуру с категориями
    keyboard = InlineKeyboardBuilder()
    
    for category, count in categories_stats.items():
        keyboard.add(InlineKeyboardButton(
            text=f"{category} ({count})",
            callback_data=f"category_{category}"
        ))
    
    keyboard.add(InlineKeyboardButton(text="🔙 Главное меню", callback_data="back_to_menu"))
    keyboard.adjust(1)  # По одной кнопке в ряд
    
    try:
        await callback.message.edit_text(
            "📦 **Каталог товаров**\n\nВыберите категорию:",
            reply_markup=keyboard.as_markup(),
            parse_mode="Markdown"
        )
    except Exception as e:
        # Если сообщение не изменилось, просто игнорируем ошибку
        pass
    await callback.answer()


@router.callback_query(F.data.startswith("category_"))
async def category_handler(callback: types.CallbackQuery):
    """Обработчик категории товаров"""
    category = callback.data.replace("category_", "")
    await show_category_products(callback, category, 0)


async def show_category_products(callback: types.CallbackQuery, category: str, page: int = 0):
    """Показать товары категории с пагинацией"""
    items_per_page = 20
    skip = page * items_per_page
    
    products = await catalog_service.get_products_by_category(category, skip, items_per_page)
    total_products = await catalog_service.get_category_products_count(category)
    
    if not products:
        await callback.message.edit_text(
            f"📦 **{category}**\n\n❌ В этой категории нет товаров.",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="🔙 К категориям", callback_data="menu_catalog")]
            ]),
            parse_mode="Markdown"
        )
        await callback.answer()
        return

    total_pages = (total_products + items_per_page - 1) // items_per_page
    
    text = f"📦 **{category}**\n\n"
    text += f"📊 Всего товаров: {total_products}\n"
    text += f"📄 Страница {page + 1} из {total_pages}\n"
    text += f"Показано: {skip + 1}-{min(skip + items_per_page, total_products)} из {total_products}\n\n"
    text += "Выберите товар для добавления в заказ:\n\n"
    
    keyboard_buttons = []
    
    # Группируем товары по 2 в ряд
    for i in range(0, len(products), 2):
        row = []
        
        # Первый товар в ряду
        p1 = products[i]
        short_name1 = truncate_text(p1.name, 20)
        row.append(InlineKeyboardButton(
            text=f"🛒 {short_name1} - {p1.price:.0f}₸",
            callback_data=f"add_to_cart_{str(p1.id)}"
        ))
        
        # Второй товар в ряду (если есть)
        if i + 1 < len(products):
            p2 = products[i + 1]
            short_name2 = truncate_text(p2.name, 20)
            row.append(InlineKeyboardButton(
                text=f"🛒 {short_name2} - {p2.price:.0f}₸",
                callback_data=f"add_to_cart_{str(p2.id)}"
            ))
        
        keyboard_buttons.append(row)
    
    # Добавляем кнопки навигации по страницам
    nav_buttons = []
    # Используем простую замену для безопасности callback_data
    safe_category = category.replace(" ", "__SPACE__").replace(".", "__DOT__")
    if page > 0:
        nav_buttons.append(InlineKeyboardButton(text="⬅️ Назад", callback_data=f"catpage_{safe_category}_{page-1}"))
    if page < total_pages - 1:
        nav_buttons.append(InlineKeyboardButton(text="➡️ Далее", callback_data=f"catpage_{safe_category}_{page+1}"))
    
    if nav_buttons:
        keyboard_buttons.append(nav_buttons)
    
    # Добавляем кнопки возврата
    keyboard_buttons.append([
        InlineKeyboardButton(text="🔙 К категориям", callback_data="menu_catalog")
    ])
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)
    
    try:
        await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="Markdown")
    except Exception as e:
        # Если сообщение не изменилось, просто игнорируем ошибку
        pass
    await callback.answer()


@router.callback_query(F.data.startswith("catpage_"))
async def category_page_handler(callback: types.CallbackQuery):
    """Обработчик пагинации в категории"""
    parts = callback.data.split("_")
    # Декодируем категорию обратно
    safe_category = "_".join(parts[1:-1])  # Объединяем части категории (без catpage)
    category = safe_category.replace("__SPACE__", " ").replace("__DOT__", ".")
    page = int(parts[-1])
    await show_category_products(callback, category, page)


# Старые обработчики для совместимости
async def show_catalog(callback: types.CallbackQuery, page: int = 0):
    """Старый обработчик каталога - теперь перенаправляет на категории"""
    await catalog_handler(callback)


@router.callback_query(F.data.startswith("catalog_page_"))
async def catalog_page(callback: types.CallbackQuery):
    """Старый обработчик пагинации - теперь перенаправляет на категории"""
    await catalog_handler(callback)


@router.callback_query(F.data.startswith("add_to_cart_"))
async def add_to_cart(callback: types.CallbackQuery):
    product_id = callback.data.split("_")[-1]
    
    # Получаем информацию о товаре
    product = await catalog_service.get_product_by_id(product_id)
    
    if not product:
        await callback.answer("❌ Товар не найден!")
        return
    
    # Показываем меню выбора количества
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="1️⃣", callback_data=f"quantity_{product_id}_1"),
            InlineKeyboardButton(text="2️⃣", callback_data=f"quantity_{product_id}_2"),
            InlineKeyboardButton(text="3️⃣", callback_data=f"quantity_{product_id}_3")
        ],
        [
            InlineKeyboardButton(text="5️⃣", callback_data=f"quantity_{product_id}_5"),
            InlineKeyboardButton(text="🔟", callback_data=f"quantity_{product_id}_10"),
            InlineKeyboardButton(text="2️⃣0️⃣", callback_data=f"quantity_{product_id}_20")
        ],
        [
            InlineKeyboardButton(text="🔙 К каталогу", callback_data="menu_catalog")
        ]
    ])
    
    await callback.message.edit_text(
        f"🛒 <b>Добавление в заказ</b>\n\n"
        f"📦 <b>{product.name}</b>\n"
        f"💰 {product.price:.2f} ₸ за {product.package}\n\n"
        f"Выберите количество:",
        reply_markup=keyboard
    )
    await callback.answer()


@router.callback_query(F.data.startswith("quantity_"))
async def select_quantity(callback: types.CallbackQuery):
    parts = callback.data.split("_")
    product_id = parts[1]
    quantity = int(parts[2])
    
    # Получаем товар
    product = await catalog_service.get_product_by_id(product_id)
    
    if not product:
        await callback.answer("❌ Товар не найден!")
        return
    
    # Создаем заказ или добавляем к существующему
    from app.services import auth as auth_service, orders as order_service
    
    user = await auth_service.get_logged_in_user(callback.from_user.id)
    if not user:
        await callback.answer("❌ Пользователь не найден!")
        return
    
    # Создаем новый заказ
    order = await order_service.create_order(str(user.id))
    await order_service.add_item_to_order(str(order.id), product_id, quantity)
    
    # Обновляем общую сумму заказа
    total_cost = await order_service.calculate_order_total(str(order.id))
    
    await callback.message.edit_text(
        f"✅ <b>Товар добавлен в заказ!</b>\n\n"
        f"📦 <b>{product.name}</b>\n"
        f"📊 Количество: {quantity} {product.package}\n"
        f"💰 Сумма: {total_cost:.2f} ₸\n\n"
        f"🆔 Номер заказа: <code>{order.id}</code>",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="➕ Добавить еще", callback_data="menu_catalog")],
            [InlineKeyboardButton(text="🛒 Мои заказы", callback_data="menu_orders")],
            [InlineKeyboardButton(text="🏠 Главное меню", callback_data="back_to_menu")]
        ])
    )
    await callback.answer()


@router.message(Command("catalog"))
async def cmd_catalog(msg: types.Message):
    # Создаем фиктивный callback для совместимости
    fake_callback = types.CallbackQuery(
        id="fake",
        from_user=msg.from_user,
        chat_instance="fake",
        message=msg,
        data="menu_catalog"
    )
    await catalog_handler(fake_callback) 