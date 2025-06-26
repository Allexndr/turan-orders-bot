from aiogram import Router, types, F
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardRemove

from app.services import auth as auth_service

router = Router(name="auth")


class AuthStates(StatesGroup):
    waiting_login = State()
    waiting_password = State()
    waiting_reg_login = State()
    waiting_reg_password = State()


def get_welcome_keyboard():
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔑 Войти в систему", callback_data="auth_login")],
        [InlineKeyboardButton(text="📝 Создать аккаунт", callback_data="auth_register")],
        [InlineKeyboardButton(text="ℹ️ О боте", callback_data="about_bot")]
    ])
    return keyboard


@router.message(CommandStart())
async def cmd_start(msg: types.Message, state: FSMContext):
    user = await auth_service.get_logged_in_user(msg.from_user.id)
    if user:
        from app.routers.menu import show_main_menu
        await show_main_menu(msg)
        return

    welcome_text = """🎉 <b>Добро пожаловать в Turan Bot!</b>

🤖 Система управления заказами и остатками

📦 <b>Возможности:</b>
• Просмотр каталога товаров
• Создание и управление заказами  
• Учет складских остатков
• Аналитика продаж

👇 <b>Выберите действие:</b>"""
    
    await msg.answer(welcome_text, reply_markup=get_welcome_keyboard(), reply_to_message_id=None)
    # Убираем обычную клавиатуру
    await msg.answer("🔽", reply_markup=ReplyKeyboardRemove())


@router.callback_query(F.data == "auth_login")
async def start_login(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        "🔑 <b>Вход в систему</b>\n\n"
        "Введите ваш логин:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_welcome")]
        ])
    )
    await state.set_state(AuthStates.waiting_login)
    await callback.answer()


@router.callback_query(F.data == "auth_register")
async def start_register(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        "📝 <b>Регистрация нового пользователя</b>\n\n"
        "Придумайте логин (только латинские буквы и цифры):",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_welcome")]
        ])
    )
    await state.set_state(AuthStates.waiting_reg_login)
    await callback.answer()


@router.callback_query(F.data == "about_bot")
async def about_bot(callback: types.CallbackQuery):
    about_text = """ℹ️ <b>О Turan Bot</b>

🤖 <b>Что это?</b>
Профессиональная система для управления заказами и складскими остатками через Telegram.

🎯 <b>Основные функции:</b>
• 📦 Каталог товаров с ценами
• 🛒 Создание и отслеживание заказов
• 📊 Управление остатками на складе
• 📈 Аналитика продаж и отчеты
• 🤖 Автоматический расчет заказов

🔐 <b>Безопасность:</b>
• Персональная авторизация
• Защищенное хранение данных
• Индивидуальные остатки для каждого пользователя

💡 <b>Удобство:</b>
• Полностью кнопочный интерфейс
• Интуитивная навигация
• Быстрый доступ ко всем функциям"""

    await callback.message.edit_text(
        about_text,
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔙 Назад к входу", callback_data="back_to_welcome")]
        ])
    )
    await callback.answer()


@router.callback_query(F.data == "back_to_welcome")
async def back_to_welcome(callback: types.CallbackQuery, state: FSMContext):
    await state.clear()
    welcome_text = """🎉 <b>Добро пожаловать в Turan Bot!</b>

🤖 Система управления заказами и остатками

📦 <b>Возможности:</b>
• Просмотр каталога товаров
• Создание и управление заказами  
• Учет складских остатков
• Аналитика продаж

👇 <b>Выберите действие:</b>"""
    await callback.message.edit_text(welcome_text, reply_markup=get_welcome_keyboard())
    await callback.answer()


# Логин для входа
@router.message(AuthStates.waiting_login)
async def proc_login(msg: types.Message, state: FSMContext):
    await state.update_data(login=msg.text.strip())
    await msg.answer(
        "🔐 Теперь введите пароль:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔙 Отмена", callback_data="back_to_welcome")]
        ])
    )
    await state.set_state(AuthStates.waiting_password)


@router.message(AuthStates.waiting_password)
async def proc_password(msg: types.Message, state: FSMContext):
    data = await state.get_data()
    login = data["login"]
    password = msg.text.strip()

    user = await auth_service.authenticate_user(login, password)
    if user:
        # Логиним пользователя
        await auth_service.login_user(user, msg.from_user.id)
        
        await msg.answer("✅ <b>Успешная авторизация!</b>")
        await state.clear()
        
        from app.routers.menu import show_main_menu
        await show_main_menu(msg)
    else:
        await msg.answer(
            "❌ Неверный логин или пароль.\n\nПопробуйте еще раз:",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="🔙 Назад к выбору", callback_data="back_to_welcome")]
            ])
        )


# Регистрация - логин
@router.message(AuthStates.waiting_reg_login)
async def proc_reg_login(msg: types.Message, state: FSMContext):
    login = msg.text.strip()
    
    if len(login) < 3:
        await msg.answer("❌ Логин должен содержать минимум 3 символа. Попробуйте еще раз:")
        # Остаемся в том же состоянии для повторного ввода логина
        return
    
    if not login.isalnum():
        await msg.answer("❌ Логин может содержать только буквы и цифры. Попробуйте еще раз:")
        # Остаемся в том же состоянии для повторного ввода логина
        return
    
    # Проверяем, не занят ли логин
    existing_user = await auth_service.get_user_by_username(login)
    if existing_user:
        await msg.answer("❌ Этот логин уже занят. Выберите другой:")
        return
    
    await state.update_data(reg_login=login)
    print(f"DEBUG: Saved login '{login}' to state, switching to password input")
    await msg.answer(
        f"✅ Логин <b>{login}</b> свободен!\n\n"
        "🔐 Теперь придумайте пароль (минимум 4 символа):",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_welcome")]
        ])
    )
    await state.set_state(AuthStates.waiting_reg_password)


@router.message(AuthStates.waiting_reg_password)
async def proc_reg_password(msg: types.Message, state: FSMContext):
    password = msg.text.strip()
    print(f"DEBUG: Processing password, length={len(password)}")
    
    if len(password) < 4:
        await msg.answer("❌ Пароль должен содержать минимум 4 символа. Попробуйте еще раз:")
        # Остаемся в том же состоянии для повторного ввода пароля
        return
    
    data = await state.get_data()
    login = data.get("reg_login")
    
    # Проверяем, что логин сохранился в состоянии
    if not login:
        await msg.answer("❌ Произошла ошибка. Начните регистрацию заново.")
        await state.clear()
        from app.routers.auth import cmd_start
        await cmd_start(msg, state)
        return
    
    # Создаем пользователя
    try:
        print(f"DEBUG: Creating user with login='{login}', password_length={len(password)}, telegram_id={msg.from_user.id}")
        user = await auth_service.create_user(login, password)
        print(f"DEBUG: User created successfully: {user.username}")
        
        # Логиним нового пользователя
        await auth_service.login_user(user, msg.from_user.id)
        
        await msg.answer("🎉 <b>Регистрация успешно завершена!</b>")
        await state.clear()
        
        from app.routers.menu import show_main_menu
        await show_main_menu(msg)
    except ValueError as e:
        print(f"DEBUG: Registration error: {str(e)}")
        await msg.answer(f"❌ Ошибка регистрации: {str(e)}")
        await state.clear()
        # Исправляем вызов back_to_welcome
        welcome_text = """🎉 <b>Добро пожаловать в Turan Bot!</b>

🤖 Система управления заказами и остатками

📦 <b>Возможности:</b>
• Просмотр каталога товаров
• Создание и управление заказами  
• Учет складских остатков
• Аналитика продаж

👇 <b>Выберите действие:</b>"""
        await msg.answer(welcome_text, reply_markup=get_welcome_keyboard()) 