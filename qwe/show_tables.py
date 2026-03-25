import sqlite3
import os

DB_PATH = 'store.db'


def print_separator(title, char='=', length=80):
    print(f"\n{char * length}")
    print(f" {title} ")
    print(f"{char * length}")


def print_table_header(headers, col_widths):
    header_row = ""
    separator = ""
    for i, header in enumerate(headers):
        header_row += f"| {header:<{col_widths[i]}} "
        separator += f"+{'-' * (col_widths[i] + 2)}"
    header_row += "|"
    separator += "+"
    print(separator)
    print(header_row)
    print(separator)


def print_table_row(row, col_widths):
    row_str = ""
    for i, value in enumerate(row):
        if value is None:
            value = "NULL"
        elif isinstance(value, (int, float)):
            row_str += f"| {value:>{col_widths[i]}} "
        else:
            row_str += f"| {str(value):<{col_widths[i]}} "
    row_str += "|"
    print(row_str)


def get_column_widths(cursor, table_name, headers, rows, max_width=50):
    widths = []
    for i, header in enumerate(headers):
        width = len(header)
        for row in rows:
            if row[i] is not None:
                val_len = len(str(row[i]))
                if val_len > width:
                    width = min(val_len, max_width)
        widths.append(width)
    return widths


def show_table(cursor, table_name, columns, description=None):
    print_separator(table_name)
    if description:
        print(f"{description}")

    try:
        cursor.execute(f"SELECT {', '.join(columns)} FROM {table_name} LIMIT 20")
        rows = cursor.fetchall()

        if not rows:
            print("Таблица пуста")
            return

        headers = [col.split(' as ')[-1] if ' as ' in col else col for col in columns]
        col_widths = get_column_widths(cursor, table_name, headers, rows)

        print_table_header(headers, col_widths)

        for row in rows:
            print_table_row(row, col_widths)

        separator = ""
        for width in col_widths:
            separator += f"+{'-' * (width + 2)}"
        separator += "+"
        print(separator)

        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        count = cursor.fetchone()[0]
        print(f"Всего записей: {count}" + (" (показано первых 20)" if count > 20 else ""))

    except sqlite3.Error as e:
        print(f"Ошибка при чтении таблицы {table_name}: {e}")


def show_custom_query(cursor, query, title="Результат запроса"):
    print_separator(title)
    try:
        cursor.execute(query)
        rows = cursor.fetchall()

        if not rows:
            print("Нет данных")
            return

        headers = [description[0] for description in cursor.description]

        col_widths = []
        for i, header in enumerate(headers):
            width = len(header)
            for row in rows[:10]:
                if row[i] is not None:
                    val_len = len(str(row[i]))
                    if val_len > width:
                        width = min(val_len, 50)
            col_widths.append(width)

        print_table_header(headers, col_widths)
        for row in rows[:20]:
            print_table_row(row, col_widths)

        separator = ""
        for width in col_widths:
            separator += f"+{'-' * (width + 2)}"
        separator += "+"
        print(separator)
        print(f"Всего записей: {len(rows)}" + (" (показано первых 20)" if len(rows) > 20 else ""))

    except sqlite3.Error as e:
        print(f"Ошибка выполнения запроса: {e}")


def main():
    """Главная функция"""
    print("=" * 80)
    print(" ПРОСМОТР БАЗЫ ДАННЫХ ")
    print("=" * 80)
    print(f"Файл БД: {DB_PATH}")

    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        # 1. Должности
        show_table(cursor, "position",
                   ["id", "code", "title"],
                   "Справочник должностей сотрудников")

        # 2. Сотрудники (с данными из account)
        print_separator("employee")
        print("Список сотрудников")
        show_custom_query(cursor, """
            SELECT 
                e.id,
                e.full_name,
                e.inn,
                e.phone,
                a.login,
                a.email,
                a.status
            FROM employee e
            LEFT JOIN account a ON a.id = e.id
            ORDER BY e.id
        """)

        # 3. Категории прайс-листов
        show_table(cursor, "price_category",
                   ["id", "code", "name", "description"],
                   "Типы прайс-листов")

        # 4. Покупатели (с данными из account)
        print_separator("ПОКУПАТЕЛИ (с подробностями)")
        show_custom_query(cursor, """
                   SELECT 
                       p.id,
                       p.type,
                       CASE 
                           WHEN p.type = 'юр' THEN l.name
                           ELSE pr.last_name || ' ' || pr.first_name
                       END as client_name,
                       pc.name as price_category,
                       e.full_name as manager,
                       COALESCE(a.login, 'Нет логина') as login,
                       COALESCE(a.email, 'Нет email') as email,
                       a.status,
                       datetime(a.created_at, 'localtime') as created_at
                   FROM purchaser p
                   LEFT JOIN account a ON a.id = p.id
                   LEFT JOIN legal_entity l ON l.id = p.id
                   LEFT JOIN private_person pr ON pr.id = p.id
                   LEFT JOIN price_category pc ON pc.id = p.price_category_id
                   LEFT JOIN employee e ON e.id = p.manager_id
                   ORDER BY p.id
               """, "Информация о покупателях")
        # 5. Товары
        show_table(cursor, "product",
                   ["id", "article", "name", "stock_quantity", "purchase_price", "manufacturer"],
                   "Товарная номенклатура")

        # 6. Заказы
        print_separator("ЗАКАЗЫ")
        show_custom_query(cursor, """
            SELECT 
                o.id,
                o.issue_date,
                CASE 
                    WHEN p.type = 'юр' THEN l.name
                    ELSE pr.last_name || ' ' || pr.first_name
                END as client,
                e.full_name as manager,
                o.payment_date,
                o.release_date
            FROM "order" o
            LEFT JOIN purchaser p ON p.id = o.buyer_id
            LEFT JOIN legal_entity l ON l.id = p.id
            LEFT JOIN private_person pr ON pr.id = p.id
            LEFT JOIN employee e ON e.id = o.employee_id
            ORDER BY o.id
        """)

        # 7. Состав заказов
        print_separator("СОСТАВ ЗАКАЗОВ")
        show_custom_query(cursor, """
            SELECT 
                oi.order_id,
                oi.product_id,
                pr.name as product_name,
                oi.quantity,
                oi.price,
                oi.discount,
                CASE WHEN oi.is_missing = 1 THEN 'Да' ELSE 'Нет' END as is_missing,
                ROUND(oi.quantity * oi.price * (100 - oi.discount) / 100, 2) as total
            FROM order_item oi
            LEFT JOIN product pr ON pr.id = oi.product_id
            ORDER BY oi.order_id, oi.product_id
        """)

        # 8. Документы об оплате
        show_table(cursor, "payment_doc",
                   ["id", "type", "payment_time", "amount", "order_id"],
                   "Платежные документы")

        # 9. Сводная статистика
        print_separator("СТАТИСТИКА")

        cursor.execute("SELECT COUNT(*) FROM purchaser")
        total_clients = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM employee")
        total_employees = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM product")
        total_products = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM \"order\"")
        total_orders = cursor.fetchone()[0]

        cursor.execute("""
            SELECT SUM(oi.quantity * oi.price * (100 - oi.discount) / 100) as total_sales
            FROM order_item oi
        """)
        total_sales = cursor.fetchone()[0] or 0

        print(f"Статистика:")
        print(f"   • Покупателей: {total_clients}")
        print(f"   • Сотрудников: {total_employees}")
        print(f"   • Товаров: {total_products}")
        print(f"   • Заказов: {total_orders}")
        print(f"   • Общая сумма продаж: {total_sales:,.2f} руб.")

        # Товары с низкими остатками
        cursor.execute("""
            SELECT name, stock_quantity 
            FROM product 
            WHERE stock_quantity < 10 
            ORDER BY stock_quantity
        """)
        low_stock = cursor.fetchall()

        if low_stock:
            print(f"\nТовары с низкими остатками (<10 шт.):")
            for item in low_stock:
                print(f"   • {item['name']}: {item['stock_quantity']} шт.")

        # Заказы без оплаты
        cursor.execute("""
            SELECT COUNT(*) 
            FROM "order" 
            WHERE payment_date IS NULL
        """)
        unpaid_orders = cursor.fetchone()[0]

        if unpaid_orders > 0:
            print(f"\nНеоплаченных заказов: {unpaid_orders}")

        # 10. Роли сотрудников
        print_separator("РОЛИ СОТРУДНИКОВ")
        show_custom_query(cursor, """
            SELECT 
                e.full_name as employee,
                GROUP_CONCAT(p.title, ', ') as positions,
                COUNT(DISTINCT ep.position_id) as positions_count
            FROM employee e
            LEFT JOIN employee_position ep ON ep.employee_id = e.id
            LEFT JOIN position p ON p.id = ep.position_id
            GROUP BY e.id, e.full_name
            ORDER BY e.full_name
        """)

        conn.close()

    except sqlite3.Error as e:
        print(f"\nшибка подключения к БД: {e}")
        print("Убедитесь, что файл store.db существует и скрипт создания БД был запущен.")


if __name__ == '__main__':
    main()