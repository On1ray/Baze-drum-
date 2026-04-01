import sqlite3
import os

DB_PATH = 'E:\Рабочий\Учеба\БД\DB\DB\store.db'
SQL_DIR = 'E:\Рабочий\Учеба\БД\DB\DB\sql'

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

def show_query_from_file(cursor, filepath, title="Результат запроса"):
    if not os.path.exists(filepath):
        print(f"Файл {filepath} не найден.")
        return
    with open(filepath, 'r', encoding='utf-8') as f:
        query = f.read()
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

        # 2. Сотрудники (из SQL файла)
        show_query_from_file(cursor, os.path.join(SQL_DIR, '03_employees.sql'), "Список сотрудников")

        # 3. Категории прайс-листов
        show_table(cursor, "price_category",
                   ["id", "code", "name", "description"],
                   "Типы прайс-листов")

        # 4. Покупатели (из SQL файла)
        show_query_from_file(cursor, os.path.join(SQL_DIR, '04_customers.sql'), "Информация о покупателях")

        # 5. Товары
        show_table(cursor, "product",
                   ["id", "article", "name", "stock_quantity", "purchase_price", "manufacturer"],
                   "Товарная номенклатура")

        # 6. Заказы (из SQL файла)
        show_query_from_file(cursor, os.path.join(SQL_DIR, '05_orders.sql'), "Заказы")

        # 7. Состав заказов (из SQL файла)
        show_query_from_file(cursor, os.path.join(SQL_DIR, '06_order_items.sql'), "Состав заказов")

        # 8. Платежные документы
        show_table(cursor, "payment_doc",
                   ["id", "type", "payment_time", "amount", "order_id"],
                   "Платежные документы")

        # 9. Сводная статистика (из SQL файла)
        show_query_from_file(cursor, os.path.join(SQL_DIR, '07_statistics.sql'), "Статистика")

        # 10. Товары с низкими остатками (из SQL файла)
        show_query_from_file(cursor, os.path.join(SQL_DIR, '08_low_stock.sql'), "Товары с низкими остатками (<10 шт.)")

        # 11. Неоплаченные заказы (из SQL файла)
        show_query_from_file(cursor, os.path.join(SQL_DIR, '09_unpaid_orders.sql'), "Неоплаченные заказы")

        # 12. Роли сотрудников (из SQL файла)
        show_query_from_file(cursor, os.path.join(SQL_DIR, '10_employee_roles.sql'), "Роли сотрудников")

        conn.close()

    except sqlite3.Error as e:
        print(f"\nОшибка подключения к БД: {e}")
        print("Убедитесь, что файл store.db существует и скрипт создания БД был запущен.")

if __name__ == '__main__':
    main()