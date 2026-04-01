import sqlite3
import sys
import os

DB_PATH = 'E:\Рабочий\Учеба\БД\DB\DB\store.db'

def execute_sql_file(filepath, db_path=DB_PATH):
    if not os.path.exists(filepath):
        print(f"Файл {filepath} не найден.")
        return False

    with open(filepath, 'r', encoding='utf-8') as f:
        sql_script = f.read()

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    try:
        cursor.execute("PRAGMA foreign_keys = ON;")
        commands = sql_script.split(';')
        for command in commands:
            command = command.strip()
            if command:
                cursor.execute(command)
        conn.commit()
        print(f"Файл {filepath} успешно выполнен.")
    except sqlite3.Error as e:
        print(f"Ошибка при выполнении {filepath}: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()
    return True

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Использование: python run_sql.py " + DB_PATH)
        sys.exit(1)
    execute_sql_file(sys.argv[1])