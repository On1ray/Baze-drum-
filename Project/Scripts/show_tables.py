import sqlite3
import os

DB_PATH = r'E:\Рабочий\Учеба\БД\DB\DB\store.db'

def print_separator(title, char='=', length=80):
    print(f"\n{char * length}")
    print(f" {title} ")
    print(f"{char * length}")

def print_table(rows, headers, title=None):
    """Универсальная печать таблицы с выравниванием"""
    if not rows:
        print("(нет данных)")
        return
    # Вычисляем ширину колонок
    col_widths = []
    for i, header in enumerate(headers):
        width = len(header)
        for row in rows[:100]:
            val = str(row[i]) if row[i] is not None else 'NULL'
            width = max(width, len(val))
        col_widths.append(min(width, 50))
    
    # Разделитель
    sep = '+' + '+'.join('-' * (w + 2) for w in col_widths) + '+'
    # Заголовки
    header_line = '| ' + ' | '.join(h.ljust(col_widths[i]) for i, h in enumerate(headers)) + ' |'
    print(sep)
    print(header_line)
    print(sep)
    # Данные
    for row in rows:
        line = '| '
        for i, val in enumerate(row):
            val_str = str(val) if val is not None else 'NULL'
            if isinstance(val, (int, float)):
                line += val_str.rjust(col_widths[i]) + ' | '
            else:
                line += val_str.ljust(col_widths[i]) + ' | '
        print(line)
    print(sep)
    print(f"Всего записей: {len(rows)}")

def show_all_tables():
    print("=" * 80)
    print(" ПРОСМОТР ВСЕХ ТАБЛИЦ БАЗЫ ДАННЫХ (ВСЕ АТРИБУТЫ) ")
    print("=" * 80)
    print(f"Файл БД: {DB_PATH}\n")

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # Получаем список всех таблиц (исключая системные)
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name")
    tables = cursor.fetchall()

    for tbl in tables:
        table_name = tbl['name']
        # Получаем информацию о колонках
        cursor.execute(f"PRAGMA table_info('{table_name}')")
        columns_info = cursor.fetchall()
        # Формируем заголовки: имя колонки + тип + NOT NULL (кратко)
        headers = []
        for col in columns_info:
            col_name = col['name']
            col_type = col['type']
            not_null = " NOT NULL" if col['notnull'] else ""
            pk = " (PK)" if col['pk'] else ""
            headers.append(f"{col_name}{pk}{not_null}")
        # Получаем все данные
        cursor.execute(f"SELECT * FROM '{table_name}'")
        rows = cursor.fetchall()
        # Преобразуем строки Row в обычные списки для единообразия
        data = [list(row) for row in rows]
        print_separator(table_name, char='=', length=100)
        print_table(data, headers, title=table_name)

    conn.close()

if __name__ == '__main__':
    show_all_tables()