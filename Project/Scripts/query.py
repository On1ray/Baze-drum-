import sqlite3
import sys
import os

DB_PATH = r'E:\Рабочий\Учеба\БД\DB\DB\store.db'

def print_table(rows, max_col_width=50):
    """Выводит rows (список sqlite3.Row) в виде отформатированной таблицы."""
    if not rows:
        print("(нет данных)")
        return

    headers = list(rows[0].keys())
    # Определяем ширину каждой колонки
    col_widths = {}
    for h in headers:
        width = len(str(h))
        for row in rows[:100]:  # проверяем первые 100 строк для скорости
            val = str(row[h]) if row[h] is not None else 'NULL'
            width = max(width, len(val))
        col_widths[h] = min(width, max_col_width)

    # Формируем разделитель
    sep = '+' + '+'.join('-' * (col_widths[h] + 2) for h in headers) + '+'
    # Заголовок
    header_line = '| ' + ' | '.join(h.ljust(col_widths[h]) for h in headers) + ' |'
    print(sep)
    print(header_line)
    print(sep)

    # Данные
    for row in rows:
        line = '| '
        for h in headers:
            val = str(row[h]) if row[h] is not None else 'NULL'
            # Числа выравниваем вправо, остальное влево
            if isinstance(row[h], (int, float)):
                line += val.rjust(col_widths[h]) + ' | '
            else:
                line += val.ljust(col_widths[h]) + ' | '
        print(line)
    print(sep)
    print(f"Всего строк: {len(rows)}")

def run_query(filepath):
    if not os.path.exists(filepath):
        print(f"Файл {filepath} не найден.")
        return
    with open(filepath, 'r', encoding='utf-8') as f:
        sql = f.read()
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    try:
        cur.execute(sql)
        rows = cur.fetchall()
        print_table(rows)
    except sqlite3.Error as e:
        print(f"Ошибка: {e}")
    finally:
        conn.close()

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Использование: python query.py <файл.sql>")
    else:
        run_query(sys.argv[1])