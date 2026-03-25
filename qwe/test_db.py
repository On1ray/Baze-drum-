import sqlite3

conn = sqlite3.connect('store.db')
cursor = conn.cursor()

cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()
print("Созданные таблицы:")
for table in tables:
    print(f"  - {table[0]}")

cursor.execute("SELECT COUNT(*) FROM employee")
emp_count = cursor.fetchone()[0]
print(f"\nКоличество сотрудников: {emp_count}")

cursor.execute("SELECT COUNT(*) FROM product")
prod_count = cursor.fetchone()[0]
print(f"Количество товаров: {prod_count}")

print("\nМенеджеры:")
cursor.execute("""
    SELECT e.full_name, p.title
    FROM employee e
    JOIN employee_position ep ON ep.employee_id = e.id
    JOIN position p ON p.id = ep.position_id
    WHERE p.code = 'manager'
""")
for row in cursor.fetchall():
    print(f"  - {row[0]} ({row[1]})")

conn.close()