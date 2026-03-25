import sqlite3
import os
from datetime import datetime

DB_PATH = 'store.db'


def create_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # Доступ по имени колонки
    return conn


def create_tables():
    conn = create_connection()
    cursor = conn.cursor()
    create_table_sql = """
    -- Включаем поддержку внешних ключей
    PRAGMA foreign_keys = ON;

    -- Создание таблицы ACCOUNT
    CREATE TABLE IF NOT EXISTS account (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        login VARCHAR(50) UNIQUE,
        password_hash VARCHAR(50),
        email VARCHAR(50),
        created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
        status VARCHAR(10) NOT NULL CHECK (status IN ('active', 'blocked', 'pending'))
    );

    -- Создание таблицы PRICE_CATEGORY
    CREATE TABLE IF NOT EXISTS price_category (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        code VARCHAR(50) NOT NULL UNIQUE,
        name VARCHAR(50) NOT NULL,
        description TEXT
    );

    -- Создание таблицы EMPLOYEE
    CREATE TABLE IF NOT EXISTS employee (
        id INTEGER PRIMARY KEY,
        full_name VARCHAR(50) NOT NULL,
        inn VARCHAR(12) NOT NULL UNIQUE,
        passport VARCHAR(50) NOT NULL,
        birth_date DATE NOT NULL,
        gender CHAR(1) NOT NULL CHECK (gender IN ('м', 'ж')),
        phone VARCHAR(20) NOT NULL,
        FOREIGN KEY (id) REFERENCES account(id) ON DELETE CASCADE
    );

    -- Создание таблицы PURCHASER
    CREATE TABLE IF NOT EXISTS purchaser (
        id INTEGER PRIMARY KEY,
        type VARCHAR(3) NOT NULL CHECK (type IN ('юр', 'физ')),
        price_category_id INTEGER NOT NULL,
        manager_id INTEGER NOT NULL,
        FOREIGN KEY (id) REFERENCES account(id) ON DELETE CASCADE,
        FOREIGN KEY (price_category_id) REFERENCES price_category(id),
        FOREIGN KEY (manager_id) REFERENCES employee(id)
    );

    -- Создание таблицы LEGAL_ENTITY
    CREATE TABLE IF NOT EXISTS legal_entity (
        id INTEGER PRIMARY KEY,
        name VARCHAR(255) NOT NULL,
        legal_address TEXT NOT NULL,
        phone VARCHAR(20) NOT NULL,
        license_number VARCHAR(50),
        bank_details TEXT NOT NULL,
        firm_category VARCHAR(100) NOT NULL,
        FOREIGN KEY (id) REFERENCES purchaser(id) ON DELETE CASCADE
    );

    -- Создание таблицы PRIVATE_PERSON
    CREATE TABLE IF NOT EXISTS private_person (
        id INTEGER PRIMARY KEY,
        last_name VARCHAR(100) NOT NULL,
        first_name VARCHAR(100) NOT NULL,
        middle_name VARCHAR(100),
        birth_year INTEGER NOT NULL CHECK (birth_year BETWEEN 1900 AND 2100),
        passport_data VARCHAR(255) NOT NULL,
        address TEXT NOT NULL,
        phone VARCHAR(20) NOT NULL,
        FOREIGN KEY (id) REFERENCES purchaser(id) ON DELETE CASCADE
    );

    -- Создание таблицы POSITION
    CREATE TABLE IF NOT EXISTS position (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        code VARCHAR(20) NOT NULL UNIQUE,
        title VARCHAR(100) NOT NULL
    );

    -- Создание таблицы EMPLOYEE_POSITION
    CREATE TABLE IF NOT EXISTS employee_position (
        employee_id INTEGER NOT NULL,
        position_id INTEGER NOT NULL,
        assignment_date DATE,
        PRIMARY KEY (employee_id, position_id),
        FOREIGN KEY (employee_id) REFERENCES employee(id) ON DELETE CASCADE,
        FOREIGN KEY (position_id) REFERENCES position(id) ON DELETE CASCADE
    );

    -- Создание таблицы PRICE_LIST
    CREATE TABLE IF NOT EXISTS price_list (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date DATE NOT NULL,
        category_id INTEGER NOT NULL,
        employee_id INTEGER NOT NULL,
        FOREIGN KEY (category_id) REFERENCES price_category(id),
        FOREIGN KEY (employee_id) REFERENCES employee(id)
    );

    -- Создание таблицы PRODUCT
    CREATE TABLE IF NOT EXISTS product (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        article VARCHAR(50) NOT NULL UNIQUE,
        name VARCHAR(255) NOT NULL,
        certificate_number VARCHAR(100),
        packaging VARCHAR(100) NOT NULL,
        manufacturer VARCHAR(255) NOT NULL,
        stock_quantity INTEGER NOT NULL DEFAULT 0 CHECK (stock_quantity >= 0),
        purchase_price DECIMAL(10,2) NOT NULL CHECK (purchase_price >= 0),
        merchandiser_id INTEGER NOT NULL,
        FOREIGN KEY (merchandiser_id) REFERENCES employee(id)
    );

    -- Создание таблицы ORDER
    CREATE TABLE IF NOT EXISTS "order" (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        issue_date DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
        payment_date DATETIME,
        release_date DATETIME,
        buyer_id INTEGER NOT NULL,
        price_list_id INTEGER NOT NULL,
        employee_id INTEGER NOT NULL,
        FOREIGN KEY (buyer_id) REFERENCES purchaser(id),
        FOREIGN KEY (price_list_id) REFERENCES price_list(id),
        FOREIGN KEY (employee_id) REFERENCES employee(id)
    );

    -- Создание таблицы ORDER_ITEM
    CREATE TABLE IF NOT EXISTS order_item (
        order_id INTEGER NOT NULL,
        product_id INTEGER NOT NULL,
        quantity INTEGER NOT NULL CHECK (quantity > 0),
        price DECIMAL(10,2) NOT NULL CHECK (price >= 0),
        discount DECIMAL(5,2) DEFAULT 0 CHECK (discount >= 0 AND discount <= 100),
        is_missing BOOLEAN NOT NULL DEFAULT 0,
        PRIMARY KEY (order_id, product_id),
        FOREIGN KEY (order_id) REFERENCES "order"(id) ON DELETE CASCADE,
        FOREIGN KEY (product_id) REFERENCES product(id)
    );

    -- Создание таблицы PAYMENT_DOC
    CREATE TABLE IF NOT EXISTS payment_doc (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        type VARCHAR(20) NOT NULL CHECK (type IN ('наличный', 'безналичный')),
        payment_time DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
        amount DECIMAL(10,2) NOT NULL CHECK (amount >= 0),
        order_id INTEGER NOT NULL UNIQUE,
        FOREIGN KEY (order_id) REFERENCES "order"(id) ON DELETE CASCADE
    );
    """

    try:
        for statement in create_table_sql.split(';'):
            if statement.strip():
                cursor.execute(statement)
        conn.commit()
        print("Таблицы успешно созданы!")
    except sqlite3.Error as e:
        print(f"Ошибка при создании таблиц: {e}")
        conn.rollback()
    finally:
        conn.close()


def insert_test_data():
    conn = create_connection()
    cursor = conn.cursor()

    try:
        print("Добавление должностей...")
        positions = [
            ('manager', 'Менеджер'),
            ('merchandiser', 'Товаровед'),
            ('cashier', 'Кассир'),
            ('head', 'Заведующий')
        ]
        cursor.executemany(
            "INSERT OR REPLACE INTO position (code, title) VALUES (?, ?)",
            positions
        )

        print("Добавление категорий прайс-листов...")
        categories = [
            ('retail', 'Розничный', 'Для розничных покупателей'),
            ('wholesale', 'Оптовый', 'Для оптовых покупателей'),
            ('professional', 'Профессиональный', 'Для профессиональных клиентов')
        ]
        cursor.executemany(
            "INSERT OR REPLACE INTO price_category (code, name, description) VALUES (?, ?, ?)",
            categories
        )

        print("Добавление аккаунтов сотрудников...")
        employee_accounts = [
            (1, 'ivanov', 'hash_123', 'ivanov@store.ru', '2024-01-01 10:00:00', 'active'),
            (2, 'petrova', 'hash_456', 'petrova@store.ru', '2024-01-02 11:00:00', 'active'),
            (3, 'sidorov', 'hash_789', 'sidorov@store.ru', '2024-01-03 12:00:00', 'active'),
            (4, 'kuznecova', 'hash_111', 'kuznecova@store.ru', '2024-01-04 13:00:00', 'active')
        ]

        for acc in employee_accounts:
            cursor.execute("""
                    INSERT OR REPLACE INTO account (id, login, password_hash, email, created_at, status)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, acc)

        print("Добавление сотрудников...")
        employees = [
            (1, 'Иванов Иван Иванович', '123456789012', '4512 123456', '1985-05-15', 'м', '+79123456789'),
            (2, 'Петрова Мария Сергеевна', '234567890123', '4512 234567', '1990-08-22', 'ж', '+79234567890'),
            (3, 'Сидоров Алексей Петрович', '345678901234', '4512 345678', '1982-03-10', 'м', '+79345678901'),
            (4, 'Кузнецова Анна Владимировна', '456789012345', '4512 456789', '1978-11-30', 'ж', '+79456789012')
        ]

        for emp in employees:
            cursor.execute("""
                    INSERT OR REPLACE INTO employee (id, full_name, inn, passport, birth_date, gender, phone)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, emp)

        print(" Назначение должностей сотрудникам...")
        employee_positions = [
            (1, 1, '2023-01-15'),  # Иванов - менеджер
            (2, 2, '2023-01-20'),  # Петрова - товаровед
            (3, 1, '2023-02-01'),  # Сидоров - менеджер
            (4, 4, '2023-01-10'),  # Кузнецова - заведующий
            (2, 3, '2023-06-01')  # Петрова - также кассир
        ]

        cursor.executemany("""
                INSERT OR REPLACE INTO employee_position (employee_id, position_id, assignment_date)
                VALUES (?, ?, ?)
            """, employee_positions)

        print("Добавление аккаунтов покупателей...")
        purchaser_accounts = [
            (5, 'tehno_prom', 'hash_tehno', 'tehno@prom.ru', '2024-01-10 14:00:00', 'active'),
            (6, None, None, None, '2024-01-15 15:00:00', 'active'),
            (7, 'roznichok', 'hash_rozn', 'roznichok@mail.ru', '2024-01-20 16:00:00', 'active')
        ]

        for acc in purchaser_accounts:
            cursor.execute("""
                    INSERT OR REPLACE INTO account (id, login, password_hash, email, created_at, status)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, acc)

        print("Добавление покупателей...")
        purchasers = [
            (5, 'юр', 2, 1),  # юрлицо, оптовый прайс, менеджер Иванов
            (6, 'физ', 1, 3),  # физлицо, розничный прайс, менеджер Сидоров
            (7, 'физ', 3, 1)  # физлицо, проф. прайс, менеджер Иванов
        ]

        cursor.executemany("""
                INSERT OR REPLACE INTO purchaser (id, type, price_category_id, manager_id)
                VALUES (?, ?, ?, ?)
            """, purchasers)

        print("Добавление юридических лиц...")
        cursor.execute("""
                INSERT OR REPLACE INTO legal_entity (id, name, legal_address, phone, bank_details, firm_category)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (5, 'ООО "ТехноПром"', 'г. Москва, ул. Ленина, д. 10', '+74951234567',
                  'р/с 40702810123456789012, БИК 044525225', 'оптовик'))

        print("Добавление частных лиц...")
        private_persons = [
            (6, 'Смирнов', 'Дмитрий', 'Александрович', 1988, '4510 987654, выдан ОВД г. Москвы',
             'г. Москва, ул. Цветочная, д. 5, кв. 12', '+79112345678'),
            (7, 'Васильева', 'Елена', 'Петровна', 1992, '4511 123456, выдан ОВД г. Санкт-Петербурга',
             'г. Санкт-Петербург, Невский пр., д. 20, кв. 45', '+79223456789')
        ]

        cursor.executemany("""
                INSERT OR REPLACE INTO private_person (id, last_name, first_name, middle_name, birth_year, passport_data, address, phone)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, private_persons)

        print("Добавление товаров...")
        products = [
            ('TV-001', 'Телевизор Samsung 55"', 'Сертификат 12345', 'шт.', 'Samsung Electronics', 15, 35000.00, 2),
            ('TV-002', 'Телевизор LG 65"', 'Сертификат 12346', 'шт.', 'LG Electronics', 8, 52000.00, 2),
            ('PH-001', 'Смартфон Xiaomi 13', 'Сертификат 12347', 'шт.', 'Xiaomi', 25, 28000.00, 2),
            ('NB-001', 'Ноутбук Asus ROG', 'Сертификат 12348', 'шт.', 'Asus', 12, 85000.00, 2),
            ('ACC-001', 'Чехол для телефона', None, 'шт.', 'Generic', 100, 500.00, 2),
            ('ACC-002', 'Зарядное устройство', None, 'шт.', 'Belkin', 45, 1200.00, 2)
        ]

        cursor.executemany("""
                INSERT OR REPLACE INTO product (article, name, certificate_number, packaging, manufacturer, stock_quantity, purchase_price, merchandiser_id)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, products)

        print(" Добавление прайс-листов...")
        price_lists = [
            (1, '2024-01-01', 1, 4),  # розничный
            (2, '2024-01-01', 2, 4),  # оптовый
            (3, '2024-01-01', 3, 4),  # профессиональный
            (4, '2024-03-01', 1, 4)  # обновлённый розничный
        ]

        cursor.executemany("""
                INSERT OR REPLACE INTO price_list (id, date, category_id, employee_id)
                VALUES (?, ?, ?, ?)
            """, price_lists)

        print("Добавление заказов...")
        orders = [
            (1, '2024-02-15 10:30:00', '2024-02-15 16:20:00', '2024-02-16 14:00:00', 5, 2, 1),  # юрлицо, оптовый
            (2, '2024-02-20 14:15:00', '2024-02-20 15:30:00', '2024-02-21 11:00:00', 6, 1, 3),  # физлицо, розничный
            (3, '2024-03-01 11:45:00', '2024-03-02 10:00:00', '2024-03-03 09:30:00', 7, 3, 1)  # физлицо, проф
        ]

        cursor.executemany("""
                INSERT OR REPLACE INTO "order" (id, issue_date, payment_date, release_date, buyer_id, price_list_id, employee_id)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, orders)

        print("Добавление состава заказов...")
        order_items = [
            # Заказ 1: юрлицо
            (1, 1, 2, 35000.00, 5.00, 0),  # 2 телевизора Samsung со скидкой 5%
            (1, 4, 1, 85000.00, 10.00, 0),  # 1 ноутбук Asus со скидкой 10%
            # Заказ 2: физлицо
            (2, 3, 1, 28000.00, 0, 0),  # 1 смартфон Xiaomi
            (2, 5, 2, 500.00, 0, 1),  # 2 чехла (отсутствовали)
            # Заказ 3: физлицо
            (3, 2, 1, 52000.00, 0, 0),  # 1 телевизор LG
            (3, 6, 3, 1200.00, 15.00, 0)  # 3 зарядки со скидкой 15%
        ]

        cursor.executemany("""
                INSERT OR REPLACE INTO order_item (order_id, product_id, quantity, price, discount, is_missing)
                VALUES (?, ?, ?, ?, ?, ?)
            """, order_items)

        print("Добавление документов об оплате...")
        payments = [
            (1, 'безналичный', '2024-02-15 16:20:00', 146500.00, 1),  # 35000*2*0.95 + 85000*0.9
            (2, 'наличный', '2024-02-20 15:30:00', 28000.00, 2),
            (3, 'наличный', '2024-03-02 10:00:00', 55060.00, 3)  # 52000 + 1200*3*0.85
        ]

        cursor.executemany("""
                INSERT OR REPLACE INTO payment_doc (id, type, payment_time, amount, order_id)
                VALUES (?, ?, ?, ?, ?)
            """, payments)

        conn.commit()
        print("\nВсе тестовые данные успешно добавлены!")

        # Вывод статистики
        cursor.execute("SELECT COUNT(*) FROM employee")
        emp_count = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM purchaser")
        pur_count = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM product")
        prod_count = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM \"order\"")
        order_count = cursor.fetchone()[0]

        print("\nИтоговая статистика:")
        print(f"   • Сотрудников: {emp_count}")
        print(f"   • Покупателей: {pur_count}")
        print(f"   • Товаров: {prod_count}")
        print(f"   • Заказов: {order_count}")

    except sqlite3.Error as e:
        print(f"Ошибка при добавлении данных: {e}")
        conn.rollback()
    finally:
        conn.close()


def test_connection():
    try:
        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT sqlite_version();")
        version = cursor.fetchone()[0]
        print(f"SQLite версия: {version}")
        print(f"База данных создана: {os.path.abspath(DB_PATH)}")
        conn.close()
        return True
    except Exception as e:
        print(f"Ошибка подключения: {e}")
        return False


if __name__ == '__main__':
    print("=== Настройка базы данных ===\n")

    # Тест подключения
    if not test_connection():
        print("Проблема с подключением. Убедитесь, что Python установлен правильно.")
        exit(1)

    print("\n--- Создание таблиц ---")
    create_tables()

    print("\n--- Добавление тестовых данных ---")
    insert_test_data()

    print("\nБаза данных готова к работе!")