from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardRemove

from app.services import auth as auth_service

router = Router(name="menu")


def get_main_menu_keyboard():
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="📦 Каталог", callback_data="menu_catalog"),
            InlineKeyboardButton(text="🛒 Заказы", callback_data="menu_orders")
        ],
        [
            InlineKeyboardButton(text="📊 Остатки", callback_data="menu_stock"),
            InlineKeyboardButton(text="📈 Аналитика", callback_data="menu_analytics")
        ],
        [
            InlineKeyboardButton(text="🤖 Автозаказ", callback_data="menu_auto_order"),
            InlineKeyboardButton(text="ℹ️ Помощь", callback_data="menu_help")
        ],
        [
            InlineKeyboardButton(text="👤 Профиль", callback_data="menu_profile")
        ]
    ])
    return keyboard


async def show_main_menu(msg: types.Message):
    user = await auth_service.get_logged_in_user(msg.from_user.id)
    if not user:
        await msg.answer("Сначала авторизуйтесь через /start")
        return

    menu_text = f"""
🏠 <b>Главное меню</b>

Добро пожаловать, <b>{user.username}</b>!

🎯 Выберите нужное действие:
    """
    
    await msg.answer(menu_text, reply_markup=get_main_menu_keyboard())
    # Убираем обычную клавиатуру
    await msg.answer("👆 Выберите действие", reply_markup=ReplyKeyboardRemove())


@router.message(Command("menu"))
async def cmd_menu(msg: types.Message):
    await show_main_menu(msg)


@router.callback_query(F.data == "back_to_menu")
async def back_to_menu(callback: types.CallbackQuery):
    print(f"DEBUG: Searching for user with telegram_id: {callback.from_user.id}")
    user = await auth_service.get_logged_in_user(callback.from_user.id)
    if not user:
        print(f"DEBUG: User not found for telegram_id: {callback.from_user.id}")
        await callback.answer("❌ Пользователь не найден! Авторизуйтесь заново через /start")
        return
        
    menu_text = f"""
🏠 <b>Главное меню</b>

Добро пожаловать, <b>{user.username}</b>!

🎯 Выберите нужное действие:
    """
    try:
        await callback.message.edit_text(menu_text, reply_markup=get_main_menu_keyboard())
    except Exception as e:
        # Если не удается обновить сообщение, отправляем новое
        await callback.message.answer(menu_text, reply_markup=get_main_menu_keyboard())
    await callback.answer()


@router.callback_query(F.data == "menu_catalog")
async def menu_catalog(callback: types.CallbackQuery):
    from app.routers.catalog import show_catalog
    await show_catalog(callback, page=0)


@router.callback_query(F.data == "menu_orders")
async def menu_orders(callback: types.CallbackQuery):
    from app.routers.order import show_orders_menu
    await show_orders_menu(callback)


@router.callback_query(F.data == "menu_stock")
async def menu_stock(callback: types.CallbackQuery):
    from app.routers.stock import show_stock_menu
    await show_stock_menu(callback, page=0)


@router.callback_query(F.data == "menu_analytics")
async def menu_analytics(callback: types.CallbackQuery):
    text = ("📈 <b>Аналитика и отчеты</b>\n\n"
            "🚧 Раздел в разработке...\n"
            "Скоро здесь будут доступны отчеты по продажам!")
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔙 Назад в меню", callback_data="back_to_menu")]
    ])
    try:
        await callback.message.edit_text(text, reply_markup=keyboard)
    except:
        await callback.message.answer(text, reply_markup=keyboard)
    await callback.answer()


@router.callback_query(F.data == "menu_auto_order")
async def menu_auto_order(callback: types.CallbackQuery):
    text = ("🤖 <b>Автоматический заказ</b>\n\n"
            "🚧 Функция в разработке...\n"
            "Скоро бот сможет автоматически рассчитывать заказы на основе продаж и остатков!")
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔙 Назад в меню", callback_data="back_to_menu")]
    ])
    try:
        await callback.message.edit_text(text, reply_markup=keyboard)
    except:
        await callback.message.answer(text, reply_markup=keyboard)
    await callback.answer()


@router.callback_query(F.data == "menu_help")
async def menu_help(callback: types.CallbackQuery):
    help_text = """
ℹ️ <b>Справка по боту</b>

<b>🎯 Основные функции:</b>
• <b>Каталог</b> - просмотр товаров с ценами
• <b>Заказы</b> - создание и управление заказами
• <b>Остатки</b> - учет товаров на складе
• <b>Аналитика</b> - отчеты по продажам

<b>🔥 Как пользоваться:</b>
1️⃣ Все действия через кнопки
2️⃣ Используйте "Назад" для навигации
3️⃣ В каталоге можно добавлять товары в заказ
4️⃣ Остатки обновляются через специальное меню

<b>💡 Подсказка:</b>
Все операции интуитивно понятны - просто следуйте подсказкам бота!
    """
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔙 Назад в меню", callback_data="back_to_menu")]
    ])
    try:
        await callback.message.edit_text(help_text, reply_markup=keyboard)
    except:
        await callback.message.answer(help_text, reply_markup=keyboard)
    await callback.answer()


@router.callback_query(F.data == "menu_profile")
async def menu_profile(callback: types.CallbackQuery):
    user = await auth_service.get_logged_in_user(callback.from_user.id)
    if not user:
        await callback.answer("❌ Пользователь не найден! Авторизуйтесь заново через /start")
        return
    
    # Определяем тип пользователя
    user_type = "Тестовый пользователь" if user.username == "test" else "Обычный пользователь"
    
    profile_text = f"""
👤 <b>Профиль пользователя</b>

<b>Имя пользователя:</b> {user.username}
<b>Тип аккаунта:</b> {user_type}
<b>Telegram ID:</b> {callback.from_user.id}
<b>Статус:</b> ✅ Авторизован

<b>📊 Статистика:</b>
• Заказов создано: В разработке
• Последний вход: Сейчас
    """
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🚪 Выйти из аккаунта", callback_data="logout")
        ],
        [
            InlineKeyboardButton(text="🗑️ Удалить аккаунт", callback_data="delete_account")
        ],
        [
            InlineKeyboardButton(text="🔙 Назад в меню", callback_data="back_to_menu")
        ]
    ])
    
    try:
        await callback.message.edit_text(profile_text, reply_markup=keyboard)
    except:
        await callback.message.answer(profile_text, reply_markup=keyboard)
    await callback.answer()


@router.callback_query(F.data == "logout")
async def logout(callback: types.CallbackQuery):
    # Выполняем выход из системы
    success = await auth_service.logout_user(callback.from_user.id)
    
    if success:
        # Показываем сообщение о выходе
        logout_text = """
🚪 <b>Выход из аккаунта</b>

Вы успешно вышли из системы!

Для повторного входа используйте команду /start
        """
        
        try:
            await callback.message.edit_text(logout_text, reply_markup=None)
        except:
            await callback.message.answer(logout_text, reply_markup=None)
        
        await callback.answer("👋 До свидания!")
        
        # Показываем стартовое окно
        welcome_text = """🎉 <b>Добро пожаловать в Turan Bot!</b>

🤖 Система управления заказами и остатками

📦 <b>Возможности:</b>
• Просмотр каталога товаров
• Создание и управление заказами  
• Учет складских остатков
• Аналитика продаж

👇 <b>Выберите действие:</b>"""
        
        from app.routers.auth import get_welcome_keyboard
        await callback.message.answer(welcome_text, reply_markup=get_welcome_keyboard())
    else:
        await callback.answer("❌ Ошибка при выходе из системы")


@router.callback_query(F.data == "delete_account")
async def delete_account_confirm(callback: types.CallbackQuery):
    confirm_text = """
🗑️ <b>Удаление аккаунта</b>

⚠️ <b>ВНИМАНИЕ!</b> Это действие необратимо!

При удалении аккаунта будут удалены:
• Ваш профиль пользователя
• Все ваши заказы
• Все ваши остатки товаров
• Вся связанная с аккаунтом информация

Вы действительно хотите удалить аккаунт?
    """
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="❌ Отмена", callback_data="menu_profile"),
            InlineKeyboardButton(text="🗑️ Да, удалить", callback_data="delete_account_confirmed")
        ]
    ])
    
    try:
        await callback.message.edit_text(confirm_text, reply_markup=keyboard)
    except:
        await callback.message.answer(confirm_text, reply_markup=keyboard)
    await callback.answer()


@router.callback_query(F.data == "delete_account_confirmed")
async def delete_account_confirmed(callback: types.CallbackQuery):
    user = await auth_service.get_logged_in_user(callback.from_user.id)
    if not user:
        await callback.answer("❌ Пользователь не найден!")
        return
    
    # Проверяем, что это не тестовый пользователь
    if user.username == "test":
        await callback.answer("❌ Тестовый аккаунт нельзя удалить!")
        return
    
    # Удаляем аккаунт
    success = await auth_service.delete_user_account(user)
    
    if success:
        delete_text = """
🗑️ <b>Аккаунт удален</b>

Ваш аккаунт и все связанные данные были успешно удалены.

Спасибо за использование Turan Bot!

Для создания нового аккаунта используйте /start
        """
        
        try:
            await callback.message.edit_text(delete_text, reply_markup=None)
        except:
            await callback.message.answer(delete_text, reply_markup=None)
        
        await callback.answer("🗑️ Аккаунт удален")
        
        # Показываем стартовое окно
        welcome_text = """🎉 <b>Добро пожаловать в Turan Bot!</b>

🤖 Система управления заказами и остатками

📦 <b>Возможности:</b>
• Просмотр каталога товаров
• Создание и управление заказами  
• Учет складских остатков
• Аналитика продаж

👇 <b>Выберите действие:</b>"""
        
        from app.routers.auth import get_welcome_keyboard
        await callback.message.answer(welcome_text, reply_markup=get_welcome_keyboard())
    else:
        await callback.answer("❌ Ошибка при удалении аккаунта")
        await menu_profile(callback) 