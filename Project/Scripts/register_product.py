import sqlite3
import sys

DB_PATH = r'E:\Рабочий\Учеба\БД\DB\DB\store.db'

def register_product(article, quantity, name=None, certificate_number=None,
                     packaging=None, manufacturer=None, purchase_price=None,
                     merchandiser_id=2):
    """
    Регистрирует поступление товара. Если артикул новый - создаёт запись.
    Возвращает id товара.
    """
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    try:
        # Проверяем, существует ли товар
        cur.execute("SELECT id, stock_quantity FROM product WHERE article = ?", (article,))
        row = cur.fetchone()
        if row is None:
            # Создать новый товар
            # Обязательные поля: article, name, packaging, manufacturer, purchase_price, merchandiser_id
            if name is None or packaging is None or manufacturer is None or purchase_price is None:
                raise ValueError("Для нового товара необходимо указать name, packaging, manufacturer, purchase_price")
            cur.execute("""
                INSERT INTO product (article, name, certificate_number, packaging, manufacturer,
                                     stock_quantity, purchase_price, merchandiser_id)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (article, name, certificate_number, packaging, manufacturer,
                  quantity, purchase_price, merchandiser_id))
            product_id = cur.lastrowid
        else:
            product_id = row[0]
            old_stock = row[1]
            new_stock = old_stock + quantity
            # Обновляем только переданные поля (не NULL)
            updates = []
            params = []
            if name is not None:
                updates.append("name = ?")
                params.append(name)
            if certificate_number is not None:
                updates.append("certificate_number = ?")
                params.append(certificate_number)
            if packaging is not None:
                updates.append("packaging = ?")
                params.append(packaging)
            if manufacturer is not None:
                updates.append("manufacturer = ?")
                params.append(manufacturer)
            if purchase_price is not None:
                updates.append("purchase_price = ?")
                params.append(purchase_price)
            if merchandiser_id is not None:
                updates.append("merchandiser_id = ?")
                params.append(merchandiser_id)
            # Обязательно увеличиваем stock_quantity
            updates.append("stock_quantity = ?")
            params.append(new_stock)
            params.append(product_id)
            cur.execute(f"UPDATE product SET {', '.join(updates)} WHERE id = ?", params)

        conn.commit()
        print(f"Товар обработан. ID={product_id}")
        return product_id
    except Exception as e:
        print(f"Ошибка: {e}")
        conn.rollback()
        return None
    finally:
        conn.close()

if __name__ == '__main__':
    # Парсинг аргументов: минимально article и quantity
    if len(sys.argv) < 3:
        print("Использование: python register_product.py <article> <quantity> [name] [certificate_number] [packaging] [manufacturer] [purchase_price] [merchandiser_id]")
        sys.exit(1)
    article = sys.argv[1]
    quantity = int(sys.argv[2])
    name = sys.argv[3] if len(sys.argv) > 3 else None
    cert = sys.argv[4] if len(sys.argv) > 4 else None
    packaging = sys.argv[5] if len(sys.argv) > 5 else None
    manufacturer = sys.argv[6] if len(sys.argv) > 6 else None
    price = float(sys.argv[7]) if len(sys.argv) > 7 else None
    merch_id = int(sys.argv[8]) if len(sys.argv) > 8 else 2
    register_product(article, quantity, name, cert, packaging, manufacturer, price, merch_id)