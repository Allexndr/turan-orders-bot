import asyncio
import pandas as pd
from app.database import connect_to_mongo, close_mongo_connection
from app.services.auth import create_user
from app.services.catalog import create_product
from app.services.stock import create_stock_for_all_products


async def load_excel_data():
    """Загрузка данных из Excel в MongoDB"""
    print("Подключение к MongoDB...")
    await connect_to_mongo()
    
    try:
        # Создаем тестовых пользователей
        print("Создание тестовых пользователей...")
        try:
            await create_user("test", "test")
            print("Создан пользователь: test/test")
        except ValueError:
            print("Пользователь test уже существует")
        
        try:
            await create_user("testuser", "password123")
            print("Создан пользователь: testuser/password123")
        except ValueError:
            print("Пользователь testuser уже существует")
        
        # Создаем тестовые продукты вместо загрузки из Excel
        print("Создание тестовых продуктов...")
        test_products = [
            ("Хлеб белый", "шт", 250.0),
            ("Молоко 1л", "шт", 380.0),
            ("Масло сливочное", "кг", 600.0),
            ("Яйца куриные", "десяток", 480.0),
            ("Сыр твердый", "кг", 900.0),
            ("Мука пшеничная", "кг", 200.0),
            ("Сахар", "кг", 300.0),
            ("Соль поваренная", "кг", 150.0),
            ("Рис", "кг", 350.0),
            ("Гречка", "кг", 400.0),
        ]
        
        loaded_count = 0
        for name, package, price in test_products:
            try:
                # Создаем продукт
                product = await create_product(name, package, price)
                loaded_count += 1
                print(f"Создан продукт: {name} - {price}₸")
                    
            except Exception as e:
                print(f"Ошибка при создании продукта {name}: {e}")
                continue
        
        print(f"Успешно загружено {loaded_count} продуктов")
        
        # Создаем записи остатков для всех продуктов для тестовых пользователей
        print("Создание записей остатков...")
        from app.services.auth import get_user_by_username
        
        test_user = await get_user_by_username("test")
        if test_user:
            await create_stock_for_all_products(str(test_user.id), 0)
            print("Созданы записи остатков для пользователя test")
        
        testuser = await get_user_by_username("testuser")
        if testuser:
            await create_stock_for_all_products(str(testuser.id), 0)
            print("Созданы записи остатков для пользователя testuser")
        
        print("✅ Загрузка данных завершена!")
        
    except Exception as e:
        print(f"❌ Ошибка при загрузке: {e}")
    finally:
        await close_mongo_connection()


if __name__ == "__main__":
    asyncio.run(load_excel_data()) 