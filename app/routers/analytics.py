from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from app.services import analytics as analytics_service
from app.services.auth import get_logged_in_user

router = Router(name="analytics")


@router.callback_query(F.data == "menu_analytics")
async def analytics_handler(callback: types.CallbackQuery):
    """Обработчик аналитики"""
    user = await get_logged_in_user(callback.from_user.id)
    if not user:
        await callback.message.edit_text("❌ Вы не авторизованы. Используйте /start для входа.")
        return
    
    # Получаем аналитические данные
    analytics_data = await analytics_service.get_analytics_data()
    
    # Формируем текст отчета
    text = "📊 **Аналитика системы**\n\n"
    
    # Основные метрики
    text += "📈 **Основные показатели:**\n"
    text += f"👥 Пользователей: {analytics_data['total_users']}\n"
    text += f"📦 Товаров: {analytics_data['total_products']}\n"
    text += f"🛒 Заказов: {analytics_data['total_orders']}\n"
    text += f"💰 **Общая сумма заказов: {analytics_data['total_revenue']:.2f} ₸**\n"
    text += f"📊 Остаток товаров: {analytics_data['total_stock']}\n\n"
    
    # Статистика по категориям
    if analytics_data['categories_stats']:
        text += "🏷️ **Товары по категориям:**\n"
        for category, count in analytics_data['categories_stats'].items():
            text += f"• {category}: {count}\n"
        text += "\n"
    
    # Статистика за последние дни
    if analytics_data['daily_stats']:
        text += "📅 **Активность за последние дни:**\n"
        for date, stats in list(analytics_data['daily_stats'].items())[-3:]:  # Показываем последние 3 дня
            text += f"• {date}: {stats['orders']} заказов, {stats['revenue']:.2f} ₸\n"
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔄 Обновить", callback_data="menu_analytics")],
        [InlineKeyboardButton(text="🔙 Главное меню", callback_data="back_to_menu")]
    ])
    
    await callback.message.edit_text(
        text,
        reply_markup=keyboard,
        parse_mode="Markdown"
    )
    await callback.answer()


@router.message(Command("analytics"))
async def cmd_analytics(msg: types.Message):
    """Команда аналитики"""
    # Создаем фиктивный callback для совместимости
    fake_callback = types.CallbackQuery(
        id="fake",
        from_user=msg.from_user,
        chat_instance="fake",
        message=msg,
        data="menu_analytics"
    )
    await analytics_handler(fake_callback)


@router.message(Command("sales"))
async def sales_stats(msg: types.Message):
    """Статистика продаж"""
    total_sum = await analytics_service.get_total_orders_sum()
    await msg.answer(f"💰 **Общая сумма всех заказов: {total_sum:.2f} ₸**", parse_mode="Markdown") 