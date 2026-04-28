import sqlite3
import sys
import os

DB_PATH = r'E:\Рабочий\Учеба\БД\DB\DB\store.db'

def execute_sql_script(filepath):
    if not os.path.exists(filepath):
        print(f"Файл {filepath} не найден.")
        return False
    with open(filepath, 'r', encoding='utf-8') as f:
        sql_script = f.read()
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        conn.executescript(sql_script)   # выполняет весь скрипт целиком
        conn.commit()
        print(f"Скрипт {filepath} успешно выполнен.")
    except sqlite3.Error as e:
        print(f"Ошибка при выполнении {filepath}: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()
    return True

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Использование: python execute_sql_script.py <файл.sql>")
        sys.exit(1)
    execute_sql_script(sys.argv[1])