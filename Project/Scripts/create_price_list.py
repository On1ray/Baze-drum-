import sqlite3
import sys

DB_PATH = r'E:\Рабочий\Учеба\БД\DB\DB\store.db'

def create_price_list(category_id, percent):
    """
    Создаёт новый прайс-лист на текущую дату для указанной категории.
    percent: положительный — наценка, отрицательный — скидка (например, +10, -5).
    """
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    try:
        # 1. Найти самый свежий прайс-лист этой категории
        cur.execute("""
            SELECT id FROM price_list
            WHERE category_id = ?
            ORDER BY date DESC LIMIT 1
        """, (category_id,))
        last_pl = cur.fetchone()
        if not last_pl:
            print(f"Нет прайс-листов для категории {category_id}")
            return None

        last_pl_id = last_pl[0]

        # 2. Создать новый прайс-лист с текущей датой
        cur.execute("""
            INSERT INTO price_list (date, category_id, employee_id)
            VALUES (date('now'), ?, 4)
        """, (category_id,))
        new_pl_id = cur.lastrowid

        # 3. Скопировать товары из последнего прайс-листа, изменив цены
        cur.execute("""
            SELECT product_id, price FROM price_list_product
            WHERE price_list_id = ?
        """, (last_pl_id,))
        products = cur.fetchall()

        for product_id, old_price in products:
            new_price = old_price * (1 + percent / 100)
            # округление до десятков рублей
            new_price = round(new_price / 10) * 10
            cur.execute("""
                INSERT INTO price_list_product (price_list_id, product_id, price)
                VALUES (?, ?, ?)
            """, (new_pl_id, product_id, new_price))

        conn.commit()
        print(f"Создан новый прайс-лист id={new_pl_id} для категории {category_id}")
        return new_pl_id
    except sqlite3.Error as e:
        print(f"Ошибка: {e}")
        conn.rollback()
        return None
    finally:
        conn.close()

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("Использование: python create_price_list.py <category_id> <percent>")
        sys.exit(1)
    cat_id = int(sys.argv[1])
    percent = float(sys.argv[2])
    create_price_list(cat_id, percent)