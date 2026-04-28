import sqlite3
import sys
import os

# Добавляем путь для импорта модулей
scripts_dir = os.path.dirname(os.path.abspath(__file__))
if scripts_dir not in sys.path:
    sys.path.insert(0, scripts_dir)

DB_PATH = r'E:\Рабочий\Учеба\БД\DB\DB\store.db'

def test(description, sql, expect_error=False):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    try:
        cur.execute(sql)
        conn.commit()
        if expect_error:
            print(f"{description}: ожидалась ошибка, но запрос выполнен")
        else:
            print(f"{description}: успешно (ошибки нет)")
    except sqlite3.Error as e:
        if expect_error:
            print(f"{description}: ошибка как и ожидалось: {e}")
        else:
            print(f"{description}: неожиданная ошибка: {e}")
    finally:
        conn.close()

def get_order_total(order_id):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    try:
        cur.execute("SELECT COALESCE(SUM(quantity * price * (100 - discount) / 100), 0) FROM order_item WHERE order_id = ?", (order_id,))
        return cur.fetchone()[0]
    finally:
        conn.close()

def find_suitable_order():
    """
    Находит order_id, у которого:
    - Нет платежа (payment_doc)
    - Есть хотя бы одна позиция order_item (чтобы была сумма)
    - Существует хотя бы один product_id с ценой в price_list_product для этого заказа
    Возвращает (order_id, product_id) или (None, None)
    """
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
        SELECT DISTINCT o.id, plp.product_id
        FROM "order" o
        JOIN price_list_product plp ON plp.price_list_id = o.price_list_id
        LEFT JOIN payment_doc pd ON pd.order_id = o.id
        WHERE pd.id IS NULL
        LIMIT 1
    """)
    row = cur.fetchone()
    conn.close()
    return row if row else (None, None)

def setup_test_data(order_id, product_id):
    """Удаляет только order_item для заданной пары (чтобы избежать UNIQUE constraint). Платежи не трогает."""
    if order_id is None or product_id is None:
        return
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("DELETE FROM order_item WHERE order_id = ? AND product_id = ?", (order_id, product_id))
    conn.commit()
    conn.close()

def check_trigger_exists(trigger_name):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT 1 FROM sqlite_master WHERE type='trigger' AND name=?", (trigger_name,))
    exists = cur.fetchone() is not None
    conn.close()
    if not exists:
        print(f"ВНИМАНИЕ: Триггер {trigger_name} не найден. Проверьте его создание.")
    return exists

def main():
    # Находим подходящий заказ для тестирования (без платежа)
    order_id, product_id = find_suitable_order()
    if order_id is None:
        print("Нет подходящего заказа без платежа. Убедитесь, что в БД есть заказы без payment_doc.")
        sys.exit(1)

    # Очищаем только order_item для этой пары
    setup_test_data(order_id, product_id)

    print("=== ТЕСТИРОВАНИЕ ТРИГГЕРОВ order_item ===\n")

    # 1. Успешная вставка
    test("1. Вставка корректной позиции",
         f"INSERT INTO order_item (order_id, product_id, quantity, price, discount) VALUES ({order_id}, {product_id}, 2, 5000, 10)")

    # 2. Ошибка: товар без цены
    test("2. Вставка с несуществующим product_id",
         f"INSERT INTO order_item (order_id, product_id, quantity, price, discount) VALUES ({order_id}, 99999, 1, 1000, 0)",
         expect_error=True)

    # 3. Ошибка: скидка >100%
    test("3. Вставка со скидкой 150%",
         f"INSERT INTO order_item (order_id, product_id, quantity, price, discount) VALUES ({order_id}, {product_id}, 1, 5000, 150)",
         expect_error=True)

    # 4. Обновление скидки на некорректное значение
    test("4.1 Подготовка: вставка нормальной позиции для обновления",
         f"INSERT OR REPLACE INTO order_item (order_id, product_id, quantity, price, discount) VALUES ({order_id}, {product_id}, 1, 5000, 10)")
    test("4.2 Обновление скидки до 200%",
         f"UPDATE order_item SET discount = 200 WHERE order_id = {order_id} AND product_id = {product_id}",
         expect_error=True)

    print("\n=== ТЕСТИРОВАНИЕ ТРИГГЕРОВ payment_doc ===\n")
    check_trigger_exists("check_payment_doc_insert")
    check_trigger_exists("prevent_payment_doc_delete")

    # Убедимся, что платежа для этого заказа нет (мы выбрали заказ без платежа)
    order_total = get_order_total(order_id)
    print(f"Сумма заказа {order_id}: {order_total:.2f}")

    # 6. Ошибка: сумма платежа меньше суммы заказа
    if order_total > 0:
        test("6. Платёж на сумму меньше суммы заказа",
             f"INSERT INTO payment_doc (type, payment_time, amount, order_id) VALUES ('наличный', datetime('now'), {order_total - 10}, {order_id})",
             expect_error=True)

    # 7. Корректный платёж
    test("7. Корректный платёж",
         f"INSERT INTO payment_doc (type, payment_time, amount, order_id) VALUES ('безналичный', datetime('now'), {order_total + 1000}, {order_id})")

    # 8. Запрет на удаление привязанного платежа (теперь платёж есть, должна быть ошибка)
    test("8. Удаление платежа, привязанного к заказу",
         f"DELETE FROM payment_doc WHERE order_id = {order_id}",
         expect_error=True)

    print("\n=== ТЕСТИРОВАНИЕ ПРОЦЕДУР ===\n")
    try:
        import create_price_list
        new_pl = create_price_list.create_price_list(1, 10)
        if new_pl:
            print(f"create_price_list: создан прайс-лист id={new_pl}")
        else:
            print("create_price_list: не удалось создать прайс-лист")
    except Exception as e:
        print(f"create_price_list: ошибка {e}")

    try:
        import register_product
        import random
        test_article = f"TEST_{random.randint(1000,9999)}"
        new_id = register_product.register_product(test_article, 10, "Тестовый товар", "Серт-999", "шт.", "ТестПроизводитель", 1000.00, 2)
        if new_id:
            print(f"register_product: создан товар id={new_id}")
        else:
            print("register_product: не удалось создать товар")
    except Exception as e:
        print(f"register_product: ошибка {e}")

if __name__ == '__main__':
    main()