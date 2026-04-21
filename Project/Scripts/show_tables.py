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
    col_widths = []
    for i, header in enumerate(headers):
        width = len(header)
        for row in rows[:100]:
            val = str(row[i]) if row[i] is not None else 'NULL'
            width = max(width, len(val))
        col_widths.append(min(width, 50))
    sep = '+' + '+'.join('-' * (w + 2) for w in col_widths) + '+'
    header_line = '| ' + ' | '.join(h.ljust(col_widths[i]) for i, h in enumerate(headers)) + ' |'
    print(sep)
    print(header_line)
    print(sep)
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
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name")
    tables = cursor.fetchall()

    for tbl in tables:
        table_name = tbl['name']
        cursor.execute(f"PRAGMA table_info('{table_name}')")
        columns_info = cursor.fetchall()
        headers = []
        for col in columns_info:
            col_name = col['name']
            col_type = col['type']
            not_null = " NOT NULL" if col['notnull'] else ""
            pk = " (PK)" if col['pk'] else ""
            headers.append(f"{col_name}{pk}{not_null}")
        cursor.execute(f"SELECT * FROM '{table_name}'")
        rows = cursor.fetchall()
        data = [list(row) for row in rows]
        print_separator(table_name, char='=', length=100)
        print_table(data, headers, title=table_name)

    conn.close()

if __name__ == '__main__':
    show_all_tables()