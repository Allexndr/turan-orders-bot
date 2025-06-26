import bcrypt
from typing import Optional
from bson import ObjectId
from app.models import User


async def hash_password(password: str) -> str:
    """Хеширование пароля"""
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')


async def verify_password(password: str, hashed_password: str) -> bool:
    """Проверка пароля"""
    return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))


async def create_user(username: str, password: str, telegram_id: Optional[int] = None) -> User:
    """Создание нового пользователя"""
    # Проверяем, существует ли пользователь
    existing_user = await User.find_one(User.username == username)
    if existing_user:
        raise ValueError("Пользователь с таким именем уже существует")
    
    # Хешируем пароль
    password_hash = await hash_password(password)
    
    # Создаем пользователя
    user = User(
        username=username,
        password_hash=password_hash,
        telegram_id=telegram_id
    )
    
    await user.insert()
    return user


async def authenticate_user(username: str, password: str) -> Optional[User]:
    """Аутентификация пользователя"""
    user = await User.find_one(User.username == username)
    if not user:
        return None
    
    if not await verify_password(password, user.password_hash):
        return None
    
    return user


async def get_user_by_telegram_id(telegram_id: int) -> Optional[User]:
    """Получение пользователя по Telegram ID"""
    # Сначала ищем активно залогиненного пользователя с этим telegram_id
    user = await User.find_one(
        User.telegram_id == telegram_id, 
        User.is_logged_in == True
    )
    
    print(f"DEBUG get_user_by_telegram_id: Looking for telegram_id={telegram_id}, found logged_in user: {user.username if user else None}")
    
    # Если активного не найдено, ищем любого с этим telegram_id
    if not user:
        user = await User.find_one(User.telegram_id == telegram_id)
        print(f"DEBUG get_user_by_telegram_id: Found any user with telegram_id: {user.username if user else None}")
    
    # Если пользователь не найден, проверяем есть ли тестовый пользователь "test"
    if not user:
        test_user = await User.find_one(User.username == "test")
        if test_user:
            print(f"DEBUG get_user_by_telegram_id: Returning test user for telegram_id={telegram_id}")
            # Возвращаем тестового пользователя для любого telegram_id
            return test_user
    
    return user


async def get_user_by_username(username: str) -> Optional[User]:
    """Получение пользователя по имени пользователя"""
    return await User.find_one(User.username == username)


async def update_user_telegram_id(user_id: str, telegram_id: int) -> Optional[User]:
    """Обновление Telegram ID пользователя"""
    try:
        user = await User.get(ObjectId(user_id))
        if user:
            user.telegram_id = telegram_id
            await user.save()
        return user
    except Exception:
        return None


async def login_user(user: User, telegram_id: int) -> User:
    """Вход пользователя в систему"""
    print(f"DEBUG login_user: Setting is_logged_in=True for user {user.username}, telegram_id={telegram_id}")
    
    # Для не-тестовых пользователей очищаем этот telegram_id у других пользователей
    if user.username != "test":
        # Убираем этот telegram_id у всех других пользователей
        other_users = await User.find(
            User.telegram_id == telegram_id,
            User.id != user.id
        ).to_list()
        
        for other_user in other_users:
            print(f"DEBUG login_user: Clearing telegram_id from user {other_user.username}")
            other_user.telegram_id = None
            other_user.is_logged_in = False
            await other_user.save()
        
        user.telegram_id = telegram_id
    
    user.is_logged_in = True
    await user.save()
    print(f"DEBUG login_user: User {user.username} saved with is_logged_in={user.is_logged_in}")
    return user


async def logout_user(telegram_id: int) -> bool:
    """Выход пользователя из системы"""
    user = await get_user_by_telegram_id(telegram_id)
    if user:
        user.is_logged_in = False
        if user.username != "test":  # Для обычных пользователей очищаем telegram_id
            user.telegram_id = None
        await user.save()
        return True
    return False


async def get_logged_in_user(telegram_id: int) -> Optional[User]:
    """Получение авторизованного пользователя"""
    user = await get_user_by_telegram_id(telegram_id)
    print(f"DEBUG get_logged_in_user: telegram_id={telegram_id}, user={user.username if user else None}, is_logged_in={user.is_logged_in if user else None}")
    if user and (user.is_logged_in or user.username == "test"):
        return user
    return None


async def delete_user_account(user: User) -> bool:
    """Удаление аккаунта пользователя"""
    try:
        # Удаляем связанные данные (заказы, остатки)
        from app.models import Order, OrderItem, Stock
        
        # Удаляем заказы пользователя
        orders = await Order.find(Order.user_id == str(user.id)).to_list()
        for order in orders:
            # Удаляем элементы заказа
            await OrderItem.find(OrderItem.order_id == str(order.id)).delete()
            # Удаляем сам заказ
            await order.delete()
        
        # Удаляем остатки пользователя
        await Stock.find(Stock.user_id == str(user.id)).delete()
        
        # Удаляем самого пользователя
        await user.delete()
        return True
    except Exception as e:
        print(f"Error deleting user account: {e}")
        return False 